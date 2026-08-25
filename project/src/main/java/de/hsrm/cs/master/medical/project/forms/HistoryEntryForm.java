package de.hsrm.cs.master.medical.project.forms;

import de.hsrm.cs.master.medical.project.domain.HistoryCategory;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;
import org.springframework.format.annotation.DateTimeFormat;

import java.time.LocalDate;

@Setter
@Getter
public class HistoryEntryForm {

    @NotNull(message = "{validation.history.date.notnull}")
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate date = LocalDate.now();

    @NotBlank(message = "{validation.history.title.notblank}")
    @Size(max = 255, message = "{validation.history.title.size}")
    private String title = "";

    @NotNull(message = "{validation.history.category.notnull}")
    private HistoryCategory category;

    @Size(max = 4000, message = "{validation.history.description.size}")
    private String description = "";

    @Size(max = 150, message = "{validation.patient.doctor.size}")
    private String doctor = "";

    @Size(max = 150, message = "{validation.patient.department.size}")
    private String department = "";

}
