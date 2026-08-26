package com.aidataanalyst.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.Instant;

@Entity
@Table(name = "workspaces")
public class Workspace {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 255)
    private String name;

    @Column(name = "owner_id", nullable = false)
    private Long ownerId;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected Workspace() {
    }

    public Workspace(String name, Long ownerId) {
        this.name = name;
        this.ownerId = ownerId;
        this.createdAt = Instant.now();
    }

    public Long getId() {
        return id;
    }
}
