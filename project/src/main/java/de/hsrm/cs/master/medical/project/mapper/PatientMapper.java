package de.hsrm.cs.master.medical.project.mapper;

import de.hsrm.cs.master.medical.project.domain.Allergy;
import de.hsrm.cs.master.medical.project.domain.Medication;
import de.hsrm.cs.master.medical.project.domain.Patient;
import de.hsrm.cs.master.medical.project.forms.MedicationForm;
import de.hsrm.cs.master.medical.project.forms.PatientForm;
import org.mapstruct.AfterMapping;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Mapper(componentModel = "spring")
public interface PatientMapper {

    @Mapping(target = "id", ignore = true)
    @Mapping(target = "allergies", ignore = true)
    @Mapping(target = "medications", ignore = true)
    @Mapping(target = "historyEntries", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "updatedAt", ignore = true)
    void updatePatient(PatientForm form, @MappingTarget Patient patient);

    @Mapping(target = "allergiesRaw", source = "allergies")
    PatientForm toForm(Patient patient);

    default String mapAllergies(List<Allergy> allergies) {
        return allergies.stream().map(Allergy::getName).collect(Collectors.joining("\n"));
    }

    default void mapMedications(Patient patient, PatientForm form) {
        List<MedicationForm> medicationForms = patient.getMedications().stream().map(m -> {
            MedicationForm mf = new MedicationForm();
            mf.setName(m.getName());
            mf.setDosage(m.getDosage());
            mf.setSchedule(m.getSchedule());
            return mf;
        }).collect(Collectors.toCollection(ArrayList::new));

        if (medicationForms.isEmpty()) {
            medicationForms.add(new MedicationForm());
        }

        form.setMedications(medicationForms);
    }

    @AfterMapping
    default void mapCollections(PatientForm form, @MappingTarget Patient patient) {
        patient.getAllergies().clear();
        for (String allergyName : form.parsedAllergies()) {
            patient.getAllergies().add(new Allergy(patient, allergyName));
        }

        patient.getMedications().clear();
        for (MedicationForm medicationForm : form.nonEmptyMedications()) {
            patient.getMedications().add(new Medication(patient, medicationForm.getName().trim(), medicationForm.getDosage().trim(), medicationForm.getSchedule().trim()));
        }
    }

}
