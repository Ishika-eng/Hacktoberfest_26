package com.example.demo;

import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;

public class Order {
    @NotBlank
    private String item;
    @Min(1)
    private int quantity;

    public String getItem() { return item; }
    public void setItem(String item) { this.item = item; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
}
