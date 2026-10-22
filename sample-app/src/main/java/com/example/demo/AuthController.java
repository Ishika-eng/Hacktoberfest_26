package com.example.demo;

import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AuthController {

    private final AuthenticationManager authenticationManager;

    public AuthController(AuthenticationManager authenticationManager) {
        this.authenticationManager = authenticationManager;
    }

    @PostMapping("/public/auth-check")
    public ResponseEntity<String> check(@RequestParam String username, @RequestParam String password) {
        try {
            Authentication a = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(username, password));
            return ResponseEntity.ok("authenticated " + a.getName() + " " + a.getAuthorities());
        } catch (AuthenticationException e) {
            return ResponseEntity.status(401).body("bad credentials");
        }
    }
}
