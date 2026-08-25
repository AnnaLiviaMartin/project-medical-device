package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.HistoryCategory;
import de.hsrm.cs.master.medical.project.domain.HistoryEntry;
import de.hsrm.cs.master.medical.project.domain.Patient;
import de.hsrm.cs.master.medical.project.exception.ResourceNotFoundException;
import de.hsrm.cs.master.medical.project.forms.HistoryEntryForm;
import de.hsrm.cs.master.medical.project.repository.HistoryEntryRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * Unit tests for {@link HistoryEntryService}. Both {@link HistoryEntryRepository} and the
 * collaborating {@link PatientService} are mocked.
 */
@ExtendWith(MockitoExtension.class)
class HistoryEntryServiceTest {

    @Mock
    private HistoryEntryRepository historyEntryRepository;

    @Mock
    private PatientService patientService;

    @InjectMocks
    private HistoryEntryService historyEntryService;

    private Patient patient;
    private HistoryEntry entry;

    @BeforeEach
    void setUp() {
        patient = new Patient();
        patient.setId(1L);

        entry = new HistoryEntry();
        entry.setId(10L);
        entry.setPatient(patient);
        entry.setTitle("Follow-up Visit");
    }

    @Test
    void findByPatient_delegatesToRepository_orderedByDateDesc() {
        when(historyEntryRepository.findByPatientIdOrderByDateDesc(1L)).thenReturn(List.of(entry));

        List<HistoryEntry> result = historyEntryService.findByPatient(1L);

        assertThat(result).containsExactly(entry);
        verify(historyEntryRepository).findByPatientIdOrderByDateDesc(1L);
    }

    @Test
    void getOrThrow_returnsEntry_whenPresent() {
        when(historyEntryRepository.findById(10L)).thenReturn(Optional.of(entry));

        assertThat(historyEntryService.getOrThrow(10L)).isSameAs(entry);
    }

    @Test
    void getOrThrow_throwsResourceNotFoundException_whenMissing() {
        when(historyEntryRepository.findById(999L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> historyEntryService.getOrThrow(999L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("999");
    }

    @Test
    void getOrThrowForPatient_returnsEntry_whenItBelongsToThePatient() {
        when(historyEntryRepository.findById(10L)).thenReturn(Optional.of(entry));

        assertThat(historyEntryService.getOrThrowForPatient(1L, 10L)).isSameAs(entry);
    }

    @Test
    void getOrThrowForPatient_throwsResourceNotFoundException_whenEntryBelongsToAnotherPatient() {
        when(historyEntryRepository.findById(10L)).thenReturn(Optional.of(entry));

        // entry belongs to patient 1, but we ask for patient 2 -> must not leak cross-patient data
        assertThatThrownBy(() -> historyEntryService.getOrThrowForPatient(2L, 10L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("10");
    }

    @Test
    void create_loadsPatient_buildsEntryFromForm_trimsText_andSaves() {
        when(patientService.getOrThrow(1L)).thenReturn(patient);
        when(historyEntryRepository.save(any(HistoryEntry.class))).thenAnswer(inv -> inv.getArgument(0));

        HistoryEntryForm form = new HistoryEntryForm();
        form.setDate(LocalDate.of(2026, 3, 1));
        form.setTitle("  Follow-up Visit  ");
        form.setCategory(HistoryCategory.VISIT);
        form.setDescription("  Routine check  ");
        form.setDoctor("  Dr. Klein  ");
        form.setDepartment(null);

        HistoryEntry created = historyEntryService.create(1L, form);

        assertThat(created.getPatient()).isSameAs(patient);
        assertThat(created.getDate()).isEqualTo(LocalDate.of(2026, 3, 1));
        assertThat(created.getTitle()).isEqualTo("Follow-up Visit");
        assertThat(created.getCategory()).isEqualTo(HistoryCategory.VISIT);
        assertThat(created.getDescription()).isEqualTo("Routine check");
        assertThat(created.getDoctor()).isEqualTo("Dr. Klein");
        assertThat(created.getDepartment()).isEmpty(); // null department -> ""

        verify(historyEntryRepository).save(created);
    }

    @Test
    void create_throwsResourceNotFoundException_whenPatientDoesNotExist() {
        when(patientService.getOrThrow(404L)).thenThrow(new ResourceNotFoundException("No patient found with ID 404."));

        HistoryEntryForm form = new HistoryEntryForm();
        form.setTitle("Visit");
        form.setCategory(HistoryCategory.VISIT);

        assertThatThrownBy(() -> historyEntryService.create(404L, form))
                .isInstanceOf(ResourceNotFoundException.class);

        verify(historyEntryRepository, never()).save(any());
    }
}
