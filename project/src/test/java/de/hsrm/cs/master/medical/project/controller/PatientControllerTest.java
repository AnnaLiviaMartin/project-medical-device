package de.hsrm.cs.master.medical.project.controller;

import de.hsrm.cs.master.medical.project.domain.Patient;
import de.hsrm.cs.master.medical.project.domain.PatientStatus;
import de.hsrm.cs.master.medical.project.domain.Sex;
import de.hsrm.cs.master.medical.project.forms.PatientForm;
import de.hsrm.cs.master.medical.project.mapper.PatientMapper;
import de.hsrm.cs.master.medical.project.service.HistoryEntryService;
import de.hsrm.cs.master.medical.project.service.PatientService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;

import java.time.LocalDate;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class PatientControllerTest {

    @Mock
    private PatientService patientService;

    @Mock
    private PatientMapper mapper;

    @Mock
    private HistoryEntryService historyEntryService;

    @InjectMocks
    private PatientController patientController;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(patientController)
                .setValidator(new LocalValidatorFactoryBean())
                .build();
    }

    @Test
    void list_showsAllPatients_whenNoFilterGiven() throws Exception {
        Patient anna = patient(1L, "Anna", "Becker", PatientStatus.OUTPATIENT);
        Patient mike = patient(2L, "Michael", "Roth", PatientStatus.INPATIENT);
        when(patientService.findAll()).thenReturn(List.of(anna, mike));

        mockMvc.perform(get("/patients"))
                .andExpect(status().isOk())
                .andExpect(view().name("patients/list"))
                .andExpect(model().attribute("patients", List.of(anna, mike)))
                .andExpect(model().attribute("statusFilter", "All"))
                .andExpect(model().attributeDoesNotExist("selectedPatient"));
    }

    @Test
    void list_filtersByStatus() throws Exception {
        Patient anna = patient(1L, "Anna", "Becker", PatientStatus.OUTPATIENT);
        Patient mike = patient(2L, "Michael", "Roth", PatientStatus.INPATIENT);
        when(patientService.findAll()).thenReturn(List.of(anna, mike));

        mockMvc.perform(get("/patients").param("status", "INPATIENT"))
                .andExpect(status().isOk())
                .andExpect(model().attribute("patients", List.of(mike)));
    }

    @Test
    void list_filtersBySearchQuery_caseInsensitively() throws Exception {
        Patient anna = patient(1L, "Anna", "Becker", PatientStatus.OUTPATIENT);
        Patient mike = patient(2L, "Michael", "Roth", PatientStatus.INPATIENT);
        // the controller re-queries findAll() when q is set - stub it every time it's called
        when(patientService.findAll()).thenReturn(List.of(anna, mike));

        mockMvc.perform(get("/patients").param("q", "becker"))
                .andExpect(status().isOk())
                .andExpect(model().attribute("patients", List.of(anna)))
                .andExpect(model().attribute("query", "becker"));
    }

    @Test
    void list_addsSelectedPatient_whenSelectedPatientIdGiven() throws Exception {
        Patient anna = patient(1L, "Anna", "Becker", PatientStatus.OUTPATIENT);
        when(patientService.findAll()).thenReturn(List.of(anna));
        when(patientService.getOrThrow(1L)).thenReturn(anna);

        mockMvc.perform(get("/patients").param("selectedPatientId", "1"))
                .andExpect(status().isOk())
                .andExpect(model().attribute("selectedPatient", anna));
    }

    @Test
    void newForm_showsEmptyFormWithOneMedicationRow() throws Exception {
        mockMvc.perform(get("/patients/new"))
                .andExpect(status().isOk())
                .andExpect(view().name("patients/form"))
                .andExpect(model().attribute("isEdit", false))
                .andExpect(model().attributeExists("patientForm"));
    }

    @Test
    void create_withValidData_redirectsToDetailPage_andSetsFlashMessage() throws Exception {
        Patient created = patient(5L, "Anna", "Becker", PatientStatus.OUTPATIENT);
        when(patientService.create(any())).thenReturn(created);

        mockMvc.perform(post("/patients")
                        .param("firstName", "Anna")
                        .param("lastName", "Becker")
                        .param("dateOfBirth", "1990-01-01")
                        .param("sex", "FEMALE")
                        .param("diagnosis", "Hypertension")
                        .param("status", "OUTPATIENT")
                        .param("lastVisit", "2026-01-01")
                        .param("doctor", "Dr. Klein"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/patients/5"))
                .andExpect(flash().attribute("successMessage", "Patient \"Anna Becker\" was created successfully."));

        verify(patientService).create(any());
    }

    @Test
    void create_withMissingRequiredFields_reRendersFormWithoutSaving() throws Exception {
        mockMvc.perform(post("/patients")) // no fields at all -> the remaining @NotBlank/@NotNull fail
                .andExpect(status().isOk())
                .andExpect(view().name("patients/form"))
                .andExpect(model().attribute("isEdit", false))
                .andExpect(model().attributeHasFieldErrors("patientForm", "firstName", "lastName",
                        "dateOfBirth", "sex", "diagnosis", "lastVisit", "doctor"));

        verify(patientService, never()).create(any());
    }

    @Test
    void create_withNextAppointmentBeforeLastVisit_reRendersFormWithCrossFieldError() throws Exception {
        mockMvc.perform(post("/patients")
                        .param("firstName", "Anna")
                        .param("lastName", "Becker")
                        .param("dateOfBirth", "1990-01-01")
                        .param("sex", "FEMALE")
                        .param("diagnosis", "Hypertension")
                        .param("status", "OUTPATIENT")
                        .param("lastVisit", "2026-06-01")
                        .param("nextAppointment", "2026-05-01") // before lastVisit
                        .param("doctor", "Dr. Klein"))
                .andExpect(status().isOk())
                .andExpect(view().name("patients/form"))
                .andExpect(model().attributeHasFieldErrors("patientForm", "nextAppointment"));

        verify(patientService, never()).create(any());
    }

    @Test
    void detail_addsPatientAndHistoryEntriesToModel() throws Exception {
        Patient anna = patient(1L, "Anna", "Becker", PatientStatus.OUTPATIENT);
        when(patientService.getOrThrow(1L)).thenReturn(anna);
        when(historyEntryService.findByPatient(1L)).thenReturn(List.of());

        mockMvc.perform(get("/patients/1"))
                .andExpect(status().isOk())
                .andExpect(view().name("patients/detail"))
                .andExpect(model().attribute("patient", anna))
                .andExpect(model().attribute("historyEntries", List.of()));
    }

    @Test
    void editForm_prefillsFormFromExistingPatient() throws Exception {
        Patient anna = patient(1L, "Anna", "Becker", PatientStatus.OUTPATIENT);
        when(patientService.getOrThrow(1L)).thenReturn(anna);
        when(mapper.toForm(anna)).thenReturn(new PatientForm());

        mockMvc.perform(get("/patients/1/edit"))
                .andExpect(status().isOk())
                .andExpect(view().name("patients/form"))
                .andExpect(model().attribute("isEdit", true))
                .andExpect(model().attribute("patientId", 1L));
    }

    @Test
    void update_withValidData_redirectsToDetailPage() throws Exception {
        Patient updated = patient(1L, "Anna", "Becker-Klein", PatientStatus.OUTPATIENT);
        when(patientService.update(eq(1L), any())).thenReturn(updated);

        mockMvc.perform(post("/patients/1")
                        .param("firstName", "Anna")
                        .param("lastName", "Becker-Klein")
                        .param("dateOfBirth", "1990-01-01")
                        .param("sex", "FEMALE")
                        .param("diagnosis", "Hypertension")
                        .param("status", "OUTPATIENT")
                        .param("lastVisit", "2026-01-01")
                        .param("doctor", "Dr. Klein"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/patients/1"))
                .andExpect(flash().attribute("successMessage", "Patient \"Anna Becker-Klein\" was updated successfully."));
    }

    @Test
    void update_withInvalidData_reRendersFormWithPatientId() throws Exception {
        mockMvc.perform(post("/patients/1"))
                .andExpect(status().isOk())
                .andExpect(view().name("patients/form"))
                .andExpect(model().attribute("isEdit", true))
                .andExpect(model().attribute("patientId", 1L));

        verify(patientService, never()).update(any(), any());
    }

    @Test
    void delete_removesPatient_andRedirectsToListWithFlashMessage() throws Exception {
        Patient anna = patient(1L, "Anna", "Becker", PatientStatus.OUTPATIENT);
        when(patientService.getOrThrow(1L)).thenReturn(anna);

        mockMvc.perform(post("/patients/1/delete"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/patients"))
                .andExpect(flash().attribute("successMessage", "Patient \"Anna Becker\" was deleted."));

        verify(patientService).delete(1L);
    }

    private Patient patient(Long id, String firstName, String lastName, PatientStatus status) {
        Patient patient = new Patient();
        patient.setId(id);
        patient.setFirstName(firstName);
        patient.setLastName(lastName);
        patient.setDateOfBirth(LocalDate.of(1990, 1, 1));
        patient.setSex(Sex.FEMALE);
        patient.setDiagnosis("Hypertension");
        patient.setStatus(status);
        patient.setLastVisit(LocalDate.of(2026, 1, 1));
        patient.setDoctor("Dr. Klein");
        patient.setAddressCity("Wiesbaden");
        patient.setEmergencyContactName("");
        patient.setEmergencyContactRelation("");
        patient.setEmergencyContactPhone("");
        return patient;
    }
}
