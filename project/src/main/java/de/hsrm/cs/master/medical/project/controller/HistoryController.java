package de.hsrm.cs.master.medical.project.controller;

import de.hsrm.cs.master.medical.project.domain.HistoryEntry;
import de.hsrm.cs.master.medical.project.domain.Patient;
import de.hsrm.cs.master.medical.project.domain.XRayImage;
import de.hsrm.cs.master.medical.project.exception.FileStorageException;
import de.hsrm.cs.master.medical.project.forms.FileUploadForm;
import de.hsrm.cs.master.medical.project.forms.HistoryEntryForm;
import de.hsrm.cs.master.medical.project.service.AttachmentService;
import de.hsrm.cs.master.medical.project.service.HistoryEntryService;
import de.hsrm.cs.master.medical.project.service.ImagingService;
import de.hsrm.cs.master.medical.project.service.PatientService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/patients/{patientId}/history")
public class HistoryController {

    @Autowired
    private PatientService patientService;

    @Autowired
    private HistoryEntryService historyEntryService;

    @Autowired
    private AttachmentService attachmentService;

    @Autowired
    private ImagingService imagingService;

    @GetMapping("/new")
    public String newForm(@PathVariable Long patientId, Model model) {
        Patient patient = patientService.getOrThrow(patientId);
        model.addAttribute("patient", patient);
        model.addAttribute("historyEntryForm", new HistoryEntryForm());
        return "history/form";
    }

    @PostMapping
    public String create(@PathVariable Long patientId, @Valid @ModelAttribute("historyEntryForm") HistoryEntryForm form, BindingResult bindingResult, Model model, RedirectAttributes redirectAttributes) {
        if (bindingResult.hasErrors()) {
            model.addAttribute("patient", patientService.getOrThrow(patientId));
            return "history/form";
        }

        HistoryEntry created = historyEntryService.create(patientId, form);
        redirectAttributes.addFlashAttribute("successMessage", "History entry \"" + created.getTitle() + "\" was added.");
        return "redirect:/patients/" + patientId + "/history/" + created.getId();
    }

    @GetMapping("/{entryId}")
    public String detail(@PathVariable Long patientId, @PathVariable Long entryId, Model model) {
        Patient patient = patientService.getOrThrow(patientId);
        HistoryEntry entry = historyEntryService.getOrThrowForPatient(patientId, entryId);

        model.addAttribute("patient", patient);
        model.addAttribute("entry", entry);
        model.addAttribute("attachments", attachmentService.findByHistoryEntry(entryId));
        model.addAttribute("attachmentUploadForm", new FileUploadForm());
        model.addAttribute("scanUploadForm", new FileUploadForm());

        XRayImage latestImage = null;
        if (entry.getStudy() != null && !entry.getStudy().getXrayImages().isEmpty()) {
            latestImage = entry.getStudy().getXrayImages().stream().max(java.util.Comparator.comparing(XRayImage::getUploadedAt)).orElse(null);
        }
        model.addAttribute("latestImage", latestImage);

        return "history/detail";
    }

    @PostMapping("/{entryId}/attachments")
    public String uploadAttachment(@PathVariable Long patientId, @PathVariable Long entryId, @ModelAttribute("attachmentUploadForm") FileUploadForm form, RedirectAttributes redirectAttributes) {
        try {
            if (form.getFile() == null || form.getFile().isEmpty()) {
                redirectAttributes.addFlashAttribute("errorMessage", "Please choose a file before uploading.");
            } else {
                attachmentService.upload(patientId, entryId, form.getFile());
                redirectAttributes.addFlashAttribute("successMessage", "Attachment uploaded successfully.");
            }
        } catch (FileStorageException ex) {
            redirectAttributes.addFlashAttribute("errorMessage", ex.getMessage());
        }
        return "redirect:/patients/" + patientId + "/history/" + entryId;
    }

    @PostMapping("/{entryId}/attachments/{attachmentId}/delete")
    public String deleteAttachment(@PathVariable Long patientId, @PathVariable Long entryId, @PathVariable Long attachmentId, RedirectAttributes redirectAttributes) {
        attachmentService.delete(patientId, entryId, attachmentId);
        redirectAttributes.addFlashAttribute("successMessage", "Attachment deleted.");
        return "redirect:/patients/" + patientId + "/history/" + entryId;
    }

    @PostMapping("/{entryId}/scans")
    public String uploadScan(@PathVariable Long patientId, @PathVariable Long entryId, @ModelAttribute("scanUploadForm") FileUploadForm form, RedirectAttributes redirectAttributes) {
        try {
            if (form.getFile() == null || form.getFile().isEmpty()) {
                redirectAttributes.addFlashAttribute("errorMessage", "Please choose an X-ray image before uploading.");
            } else {
                imagingService.uploadScan(patientId, entryId, form.getFile());
                redirectAttributes.addFlashAttribute("successMessage", "X-ray uploaded and analyzed (simulated analysis, see notice on the results card).");
            }
        } catch (FileStorageException ex) {
            redirectAttributes.addFlashAttribute("errorMessage", ex.getMessage());
        }
        return "redirect:/patients/" + patientId + "/history/" + entryId;
    }
}
