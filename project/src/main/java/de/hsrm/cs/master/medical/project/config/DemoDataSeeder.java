package de.hsrm.cs.master.medical.project.config;

import de.hsrm.cs.master.medical.project.domain.*;
import de.hsrm.cs.master.medical.project.repository.HistoryEntryRepository;
import de.hsrm.cs.master.medical.project.repository.PatientRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDate;

/**
 * Legt beim allerersten Start ein paar Beispielpatienten an, damit die
 * Anwendung nicht mit einer leeren Liste startet. Laeuft nur, wenn die
 * Datenbank noch leer ist - loescht also nie eigene Eingaben.
 */
@Component
public class DemoDataSeeder implements CommandLineRunner {

    @Autowired
    private PatientRepository patientRepository;

    @Autowired
    private HistoryEntryRepository historyEntryRepository;

    @Override
    public void run(String... args) {
        if (patientRepository.count() > 0) {
            return;
        }

        Patient anna = new Patient();
        anna.setFirstName("Anna");
        anna.setLastName("Becker");
        anna.setDateOfBirth(LocalDate.of(1988, 4, 12));
        anna.setSex(Sex.FEMALE);
        anna.setDiagnosis("Community-acquired pneumonia");
        anna.setStatus(PatientStatus.INPATIENT);
        anna.setLastVisit(LocalDate.now().minusDays(2));
        anna.setNextAppointment(LocalDate.now().plusDays(5));
        anna.setDoctor("Dr. Sarah Klein");
        anna.setWard("Pulmonology - Ward 3");
        anna.setAddressStreet("Ringstrasse 12");
        anna.setAddressZip("65183");
        anna.setAddressCity("Wiesbaden");
        anna.setEmergencyContactName("Peter Becker");
        anna.setEmergencyContactRelation("Spouse");
        anna.setEmergencyContactPhone("+49 611 1234567");
        anna.setInsuranceProvider("Techniker Krankenkasse");
        anna.setInsurancePolicyNumber("TK-88213-A");
        anna.getAllergies().add(new Allergy(anna, "Penicillin"));
        anna.getMedications().add(new Medication(anna, "Amoxicillin", "500mg", "3x daily"));
        anna.getMedications().add(new Medication(anna, "Paracetamol", "500mg", "as needed"));
        patientRepository.save(anna);

        HistoryEntry annaVisit = new HistoryEntry();
        annaVisit.setPatient(anna);
        annaVisit.setDate(LocalDate.now().minusDays(2));
        annaVisit.setTitle("Admission - suspected pneumonia");
        annaVisit.setCategory(HistoryCategory.VISIT);
        annaVisit.setDescription("Patient presented with fever, cough and shortness of breath. Chest X-ray ordered.");
        annaVisit.setDoctor("Dr. Sarah Klein");
        annaVisit.setDepartment("Pulmonology");
        historyEntryRepository.save(annaVisit);

        Patient michael = new Patient();
        michael.setFirstName("Michael");
        michael.setLastName("Tan");
        michael.setDateOfBirth(LocalDate.of(1975, 11, 3));
        michael.setSex(Sex.MALE);
        michael.setDiagnosis("Routine cardiology follow-up");
        michael.setStatus(PatientStatus.OUTPATIENT);
        michael.setLastVisit(LocalDate.now().minusDays(30));
        michael.setNextAppointment(LocalDate.now().plusDays(60));
        michael.setDoctor("Dr. Michael Tan");
        michael.setWard("");
        michael.setAddressStreet("Bahnhofstrasse 5");
        michael.setAddressZip("60329");
        michael.setAddressCity("Frankfurt am Main");
        michael.setEmergencyContactName("Lena Tan");
        michael.setEmergencyContactRelation("Daughter");
        michael.setEmergencyContactPhone("+49 69 9876543");
        michael.setInsuranceProvider("AOK");
        michael.setInsurancePolicyNumber("AOK-55210-M");
        michael.getMedications().add(new Medication(michael, "Ramipril", "5mg", "1x daily"));
        patientRepository.save(michael);
    }
}
