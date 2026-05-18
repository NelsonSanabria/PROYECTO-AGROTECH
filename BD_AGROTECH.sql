-- =============================================================
-- SCRIPT DE CREACIÓN DE LA BASE DE DATOS: AGROTECH_ANALYTICS
-- =============================================================

-- 1. Crear la tabla principal de inventario de árboles
-- =================================================================
-- SCRIPT DE DESPLIEGUE COMPLETO EN MYSQL: AGROTECH_ANALYTICS
-- =================================================================

-- PASO 1: Crear la base de datos (si no existe ya)
CREATE DATABASE IF NOT EXISTS agrotech_analytics
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- PASO 2: Indicarle a MySQL que vamos a trabajar dentro de esa base de datos
USE agrotech_analytics;

-- =================================================================
-- PASO 3: Creación de tablas (Usando nombres en plural)
-- =================================================================

-- 3.1. Tabla de Inventario de Árboles
CREATE TABLE IF NOT EXISTS arboles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_fruta VARCHAR(50) NOT NULL,   -- Ej: 'Naranja', 'Aguacate', 'Mango', 'Limón'
    cantidad INT NOT NULL,             -- Número de árboles en el lote
    edad_anos INT NOT NULL,            -- Edad promedio
    estado_salud VARCHAR(30) DEFAULT 'Óptimo'
) ENGINE=InnoDB;

-- 3.2. Tabla de Análisis Químicos del Suelo
CREATE TABLE IF NOT EXISTS analisis_suelos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_muestra DATE NOT NULL,
    nivel_nitrogeno VARCHAR(10),       -- 'Bajo', 'Medio', 'Alto'
    nivel_potasio VARCHAR(10),         -- 'Bajo', 'Medio', 'Alto'
    ph_suelo DECIMAL(3,2)              -- Ej: 6.50
) ENGINE=InnoDB;

-- 3.3. Tabla Relacional de Planes de Fertilización
CREATE TABLE IF NOT EXISTS planes_fertilizacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    arbol_id INT,                      -- Llave foránea hacia 'arboles'
    analisis_id INT,                   -- Llave foránea hacia 'analisis_suelos'
    fecha_programada DATE NOT NULL,
    dosis_nitrogeno_total_g FLOAT,     -- Cálculo analítico total en gramos
    dosis_potasio_total_g FLOAT,       -- Cálculo analítico total en gramos
    estado_aplicacion VARCHAR(20) DEFAULT 'Pendiente',
    
    -- Definición de Relaciones e Integridad Referencial
    FOREIGN KEY (arbol_id) REFERENCES arboles(id) ON DELETE CASCADE,
    FOREIGN KEY (analisis_id) REFERENCES analisis_suelos(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- =================================================================
-- PASO 4: Inserción de Datos de Prueba (Poblado inicial)
-- =================================================================

-- Insertar tu inventario actual de frutales
INSERT INTO arboles (tipo_fruta, cantidad, edad_anos, estado_salud) VALUES 
('Naranja', 122, 15,'Óptimo'),
('Aguacate', 8, 15, 'Regular'),
('Mango', 2, 15, 'Excelente'),
('Limón', 2, 15, 'Excelente');

-- Insertar un registro de análisis de laboratorio de la tierra
INSERT INTO analisis_suelos (fecha_muestra, nivel_nitrogeno, nivel_potasio, ph_suelo) VALUES 
(CURDATE(), 'Bajo', 'Medio', 6.20);

INSERT INTO arboles (tipo_fruta, cantidad, edad_anos, estado_salud) VALUES 
('Plátano', 5, 2, 'Óptimo'),
('Guanábana', 3, 3, 'Óptimo');

