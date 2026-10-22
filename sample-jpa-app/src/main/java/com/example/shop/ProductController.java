package com.example.shop;

import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
public class ProductController {

    private final ProductRepository products;

    public ProductController(ProductRepository products) {
        this.products = products;
    }

    @GetMapping("/products")
    public List<Product> all() {
        return products.findAll();
    }

    @GetMapping("/products/{id}")
    public Product one(@PathVariable Long id) {
        return products.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
    }

    @PostMapping("/products")
    @ResponseStatus(HttpStatus.CREATED)
    public Product create(@Valid @RequestBody Product product) {
        return products.save(product);
    }

    @DeleteMapping("/products/{id}")
    public void delete(@PathVariable Long id) {
        products.deleteById(id);
    }

    @GetMapping("/whoami")
    public String whoami(HttpServletRequest request) {
        return request.getRemoteUser() == null ? "anonymous" : request.getRemoteUser();
    }
}
