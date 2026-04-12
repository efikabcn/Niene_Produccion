-- ============================================
-- Niene Producció - Database Schema
-- ============================================
-- This file runs automatically on first container start.
-- After that, use Alembic migrations for schema changes.

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Ordres de Fabricació (OF)
-- ============================================
CREATE TABLE IF NOT EXISTS ordres_fabricacio (
    id              SERIAL PRIMARY KEY,
    of_number       VARCHAR(20) UNIQUE NOT NULL,
    codi_article    VARCHAR(20),
    nom_article     VARCHAR(100),
    ample           NUMERIC(6,1),
    fils_totals     INTEGER,
    metres          INTEGER,
    ample_plegador_mm INTEGER,
    num_faixes      INTEGER,
    teler_num       INTEGER,
    estat           VARCHAR(20) DEFAULT 'pendent',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_of_number ON ordres_fabricacio(of_number);
CREATE INDEX IF NOT EXISTS idx_of_estat ON ordres_fabricacio(estat);

-- ============================================
-- Hoja 2 - Preparació i Muntatge del Fil
-- ============================================
CREATE TABLE IF NOT EXISTS hoja2_preparacio (
    id                      SERIAL PRIMARY KEY,
    of_id                   INTEGER UNIQUE NOT NULL REFERENCES ordres_fabricacio(id),
    data                    DATE,
    hora_inici_prep         TIME,
    hora_final_prep         TIME,
    fil_traspassat_sllp     BOOLEAN,
    nom_resp_preparacio     VARCHAR(100),
    vores                   BOOLEAN,
    telomares_panama        BOOLEAN DEFAULT FALSE,
    penelope                BOOLEAN DEFAULT FALSE,
    fitxa_antiga            BOOLEAN DEFAULT FALSE,
    guia_montatge           BOOLEAN DEFAULT FALSE,
    repas_conjunt           BOOLEAN DEFAULT FALSE,
    cons_bones_condicions   BOOLEAN,
    responsables_muntar     VARCHAR(200),
    responsables_desmuntar  VARCHAR(200),
    ordidor_revisio         VARCHAR(100),
    observacions            TEXT,
    estat                   VARCHAR(20) DEFAULT 'borrador',
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Hoja 2 - Muntada (thread bundles)
-- ============================================
CREATE TABLE IF NOT EXISTS hoja2_muntada (
    id          SERIAL PRIMARY KEY,
    hoja2_id    INTEGER NOT NULL REFERENCES hoja2_preparacio(id) ON DELETE CASCADE,
    color       VARCHAR(50),
    partida     VARCHAR(20),
    proveidor   VARCHAR(20),
    n_bulto     VARCHAR(30),
    conos       INTEGER,
    pes         NUMERIC(8,2),
    ordre       INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_muntada_hoja2 ON hoja2_muntada(hoja2_id);

-- ============================================
-- Future tables (placeholders)
-- ============================================
-- hoja3_ordida        -> Fulla de Revisió: Ordida
-- hoja4_plegador      -> Fulla de Revisió: Col·locació Plegador
-- hoja5_montada       -> Esquema de Montada (seqüència de colors)
-- hoja6_programacio   -> Programació Passat de Púa
