package de.hsrm.cs.master.medical.project.controller;

import de.hsrm.cs.master.medical.project.domain.Patient;
import de.hsrm.cs.master.medical.project.forms.PatientForm;
import de.hsrm.cs.master.medical.project.service.HistoryEntryService;
import de.hsrm.cs.master.medical.project.service.PatientService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.List;

@Controller
@RequestMapping("/patients")
public class PatientController {

    @Autowired
    private PatientService patientService;

    @Autowired
    private HistoryEntryService historyEntryService;

    @GetMapping
    public String list(@RequestParam(defaultValue = "") String q, @RequestParam(defaultValue = "All") String status, @RequestParam(required = false) Long selected, Model model) {
        List<Patient> patients = patientService.findAll();

        if (!q.isBlank()) {
            patients = patientService.findAll().stream().filter(p -> p.getFullSearchInformation().toLowerCase().contains(q.toLowerCase())).toList();
        }

        if (!status.equals("All")) {
            patients = patients.stream().filter(p -> p.getStatus().getLabel().equalsIgnoreCase(status)).toList();
        }

        model.addAttribute("patients", patients);
        model.addAttribute("query", q);
        model.addAttribute("statusFilter", status);

        return "patients/list";
    }

    @GetMapping("/new")
    public String newForm(Model model) {
        PatientForm form = new PatientForm();
        form.addEmptyMedicationRow();
        model.addAttribute("patientForm", form);
        model.addAttribute("isEdit", false);
        return "patients/form";
    }

    @PostMapping
    public String create(@Valid @ModelAttribute("patientForm") PatientForm form, BindingResult bindingResult, Model model, RedirectAttributes redirectAttributes) {
        validateCrossFields(form, bindingResult);

        if (bindingResult.hasErrors()) {
            model.addAttribute("isEdit", false);
            return "patients/form";
        }

        Patient created = patientService.create(form);
        redirectAttributes.addFlashAttribute("successMessage", "Patient \"" + created.getFullName() + "\" was created successfully.");
        return "redirect:/patients/" + created.getId();
    }

    @GetMapping("/{id}")
    public String detail(@PathVariable Long id, Model model) {
        Patient patient = patientService.getOrThrow(id);
        model.addAttribute("patient", patient);
        model.addAttribute("historyEntries", historyEntryService.findByPatient(id));
        return "patients/detail";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable Long id, Model model) {
        Patient patient = patientService.getOrThrow(id);
        model.addAttribute("patientForm", patientService.toForm(patient));
        model.addAttribute("patientId", id);
        model.addAttribute("isEdit", true);
        return "patients/form";
    }

    @PostMapping("/{id}")
    public String update(@PathVariable Long id, @Valid @ModelAttribute("patientForm") PatientForm form, BindingResult bindingResult, Model model, RedirectAttributes redirectAttributes) {
        validateCrossFields(form, bindingResult);

        if (bindingResult.hasErrors()) {
            model.addAttribute("patientId", id);
            model.addAttribute("isEdit", true);
            return "patients/form";
        }

        Patient updated = patientService.update(id, form);
        redirectAttributes.addFlashAttribute("successMessage", "Patient \"" + updated.getFullName() + "\" was updated successfully.");
        return "redirect:/patients/" + updated.getId();
    }

    @PostMapping("/{id}/delete")
    public String delete(@PathVariable Long id, RedirectAttributes redirectAttributes) {
        Patient patient = patientService.getOrThrow(id);
        patientService.delete(id);
        redirectAttributes.addFlashAttribute("successMessage", "Patient \"" + patient.getFullName() + "\" was deleted.");
        return "redirect:/patients";
    }

    private void validateCrossFields(PatientForm form, BindingResult bindingResult) {
        if (!form.isNextAppointmentValid()) {
            bindingResult.rejectValue("nextAppointment", "nextAppointment.beforeLastVisit", "Next appointment cannot be before the last visit.");
        }
    }
}
