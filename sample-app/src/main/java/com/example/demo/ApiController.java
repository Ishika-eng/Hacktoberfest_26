package com.example.demo;

import javax.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
public class ApiController {

    @GetMapping("/public/ping")
    public String ping() { return "pong"; }

    @GetMapping("/admin/secret")
    public String secret() { return "top-secret"; }

    @PostMapping("/orders")
    public String order(@Valid @RequestBody Order order) {
        return "ordered " + order.getQuantity() + " x " + order.getItem();
    }
}
