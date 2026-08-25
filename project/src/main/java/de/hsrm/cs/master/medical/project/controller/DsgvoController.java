package de.hsrm.cs.master.medical.project.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/dsgvo")
public class DsgvoController {

    @GetMapping("/impressum")
    public String impressum() {
        return "dsgvo/impressum";
    }

    @GetMapping("/datenschutzerklaerung")
    public String datenschutzerklaerung() {
        return "dsgvo/datenschutzerklaerung";
    }
}
