/* ========================================================================== */
/* SECCIÓN 1: LIMPIEZA TOTAL (RESET)                                          */
/* ========================================================================== */
DROP VIEW IF EXISTS V_GLOBAL_CUENTAS;
DROP TABLE IF EXISTS INV_PAGO_INTERES;
DROP TABLE IF EXISTS INV_MOVIMIENTO;
DROP TABLE IF EXISTS INV_INVERSION;
DROP TABLE IF EXISTS INV_PRODUCTO;
DROP TABLE IF EXISTS TRANSACCIONES;
DROP TABLE IF EXISTS TARJETA_CREDITO;
DROP TABLE IF EXISTS TARJETA_DEBITO;
DROP TABLE IF EXISTS CUENTA_AHORROS;
DROP TABLE IF EXISTS CUENTA_CORRIENTE;
DROP TABLE IF EXISTS CAJERO;
DROP TABLE IF EXISTS PERSONA_JURIDICA;
DROP TABLE IF EXISTS PERSONA_NATURAL;

/* ========================================================================== */
/* SECCIÓN 2: BASE DE DATOS ORIGINAL (Cimientos del Banco)                    */
/* ========================================================================== */

CREATE TABLE CAJERO (
   ID_CAJERO             SERIAL NOT NULL, -- Cambiado a SERIAL para auto-increment
   LATITUD               DECIMAL(8,2) NOT NULL,
   LONGITUD              DECIMAL(8,2) NOT NULL,
   ACTIVO                BOOL NOT NULL,
   SALDO                 DECIMAL(8,2) NOT NULL,
   DEPOSITOS             BOOL NOT NULL,
   NOMBRE                VARCHAR(20) NOT NULL,
   CIUDAD                VARCHAR(32) NOT NULL,
   PROVINCIA             VARCHAR(32) NOT NULL,
   DIRECCION             VARCHAR(128) NOT NULL,
   HORA_APERTURA         TIME NOT NULL, -- Cambiado a TIME
   HORA_CIERRE           TIME NOT NULL, -- Cambiado a TIME
   DIAS                  CHAR(1) NOT NULL,
   CONSTRAINT PK_CAJERO PRIMARY KEY (ID_CAJERO)
);

CREATE TABLE PERSONA_NATURAL (
   ID                    SERIAL NOT NULL,
   CEDULA                VARCHAR(20) NOT NULL UNIQUE,
   CELULAR               VARCHAR(20) NOT NULL,
   CORREO                VARCHAR(50) NOT NULL,
   PATRIMONIO            FLOAT8 NOT NULL,
   NOMBRE                VARCHAR(50) NOT NULL,
   APELLIDO              VARCHAR(50) NOT NULL,
   FECHA_NACIMIENTO      DATE NOT NULL,
   GENERO                VARCHAR(10) NOT NULL,
   ESTADO_CIVIL          VARCHAR(20) NOT NULL,
   OCUPACION             VARCHAR(20) NOT NULL,
   NACIONALIDAD          VARCHAR(20) NOT NULL,
   CONSTRAINT PK_PERSONA_NATURAL PRIMARY KEY (ID)
);

CREATE TABLE PERSONA_JURIDICA (
   ID                    SERIAL NOT NULL,
   RUC                   CHAR(13) NOT NULL UNIQUE,
   CELULAR               VARCHAR(20) NOT NULL,
   CORREO                VARCHAR(50) NOT NULL,
   PATRIMONIO            FLOAT8 NOT NULL,
   RAZON_SOCIAL          VARCHAR(100) NOT NULL,
   NOMBRE_COMERCIAL      VARCHAR(100) NOT NULL,
   FECHA_CONSTITUCION    DATE NOT NULL,
   TIPO_EMPRESA          VARCHAR(50) NOT NULL,
   CONSTRAINT PK_PERSONA_JURIDICA PRIMARY KEY (ID)
);

CREATE TABLE CUENTA_AHORROS (
   ID_CUENTA             SERIAL NOT NULL, -- Serial
   ID_TIPO_CUENTA        INT4 NOT NULL DEFAULT 1,
   ID_CLIENTE            INT4 NULL, -- Unificado nombre para claridad
   N_CUENTA              VARCHAR(20) NOT NULL UNIQUE, -- Varchar para evitar problemas
   ESTADO                VARCHAR(64) NOT NULL,
   SALDO_ACTUAL          DECIMAL(18,2) NOT NULL,
   FECHA_CREACION        DATE DEFAULT CURRENT_DATE,
   CONSTRAINT PK_CUENTA_AHORROS PRIMARY KEY (ID_CUENTA),
   CONSTRAINT FK_AHORRO_NATURAL FOREIGN KEY (ID_CLIENTE) REFERENCES PERSONA_NATURAL(ID)
);

CREATE TABLE CUENTA_CORRIENTE (
   ID_CUENTA             SERIAL NOT NULL, -- Serial
   ID_CLIENTE            INT4 NULL,
   N_CUENTA              VARCHAR(20) NOT NULL UNIQUE,
   ESTADO                VARCHAR(64) NOT NULL,
   SALDO_ACTUAL          DECIMAL(18,2) NOT NULL,
   FECHA_CREACION        DATE DEFAULT CURRENT_DATE,
   CONSTRAINT PK_CUENTA_CORRIENTE PRIMARY KEY (ID_CUENTA),
   CONSTRAINT FK_CORRIENTE_NATURAL FOREIGN KEY (ID_CLIENTE) REFERENCES PERSONA_NATURAL(ID)
);

/* NOTA: Omití Tarjetas y Transacciones originales por brevedad y porque 
   no son vitales para tu modulo de Inversiones, pero puedes agregarlas si gustas */

/* ========================================================================== */
/* SECCIÓN 3: CAPA DE ADAPTACIÓN (Vital para Grupo 5)                         */
/* ========================================================================== */

/* VISTA MAESTRA DE CUENTAS 
   Esto permite que Python vea todas las cuentas en un solo lugar.
   Si el cliente tiene Ahorros o Corriente, aquí salen ambas. */
CREATE OR REPLACE VIEW V_GLOBAL_CUENTAS AS
SELECT 
    'AHORROS' as TIPO_CUENTA,
    ID_CUENTA as ID_INTERNO,
    N_CUENTA,
    ID_CLIENTE,
    SALDO_ACTUAL
FROM CUENTA_AHORROS
UNION ALL
SELECT 
    'CORRIENTE' as TIPO_CUENTA,
    ID_CUENTA as ID_INTERNO,
    N_CUENTA,
    ID_CLIENTE,
    SALDO_ACTUAL
FROM CUENTA_CORRIENTE;

/* ========================================================================== */
/* SECCIÓN 4: MÓDULO DE INVERSIONES (Tu Responsabilidad)                      */
/* ========================================================================== */

/* 1. Catálogo de Productos (PlazoDolar vs ArmaDolar) */
CREATE TABLE INV_PRODUCTO (
    ID_PRODUCTO     SERIAL PRIMARY KEY,
    CODIGO          VARCHAR(20) NOT NULL, -- 'PLAZODOLAR', 'ARMADOLAR'
    NOMBRE          VARCHAR(50) NOT NULL,
    TASA_ANUAL      DECIMAL(5,2) NOT NULL,
    MONTO_MIN       DECIMAL(12,2) NOT NULL,
    DIAS_MIN        INT NOT NULL,
    ES_FLEXIBLE     BOOLEAN NOT NULL -- TRUE = Permite abonos (ArmaDolar)
);

/* 2. La Inversión del Cliente */
CREATE TABLE INV_INVERSION (
    ID_INVERSION    SERIAL PRIMARY KEY,
    ID_CLIENTE      INT NOT NULL,
    ID_PRODUCTO     INT REFERENCES INV_PRODUCTO(ID_PRODUCTO),
    
    -- De dónde salió la plata
    CUENTA_ORIGEN_NUM VARCHAR(20) NOT NULL, 
    
    MONTO_CAPITAL   DECIMAL(12,2) NOT NULL,
    FECHA_INICIO    DATE DEFAULT CURRENT_DATE,
    FECHA_VENCIMIENTO DATE NOT NULL,
    
    -- Estados: 'ACTIVA', 'FINALIZADA', 'CANCELADA_ANTICIPADA'
    ESTADO          VARCHAR(30) DEFAULT 'ACTIVA',
    
    GANANCIA_PROYECTADA DECIMAL(12,2) NOT NULL,
    
    CONSTRAINT FK_INV_CLIENTE FOREIGN KEY (ID_CLIENTE) REFERENCES PERSONA_NATURAL(ID)
);

/* 3. Historial de Movimientos de Inversión 
   (Aquí se registran los débitos iniciales y los pagos finales) */
CREATE TABLE INV_MOVIMIENTO (
    ID_MOVIMIENTO   SERIAL PRIMARY KEY,
    ID_INVERSION    INT REFERENCES INV_INVERSION(ID_INVERSION),
    TIPO            VARCHAR(30) NOT NULL, -- 'DEPOSITO_INICIAL', 'ABONO_EXTRA', 'PAGO_INTERES', 'PENALIZACION'
    MONTO           DECIMAL(12,2) NOT NULL,
    FECHA           TIMESTAMP DEFAULT NOW(),
    DESCRIPCION     VARCHAR(150)
);

/* ========================================================================== */
/* SECCIÓN 5: DATOS SEMILLA (Para que puedan trabajar HOY)                    */
/* ========================================================================== */

/* A. Creamos los productos de Pichincha */
INSERT INTO INV_PRODUCTO (CODIGO, NOMBRE, TASA_ANUAL, MONTO_MIN, DIAS_MIN, ES_FLEXIBLE) VALUES
('PLAZODOLAR', 'Plazo Dólar', 6.50, 500.00, 31, FALSE),
('ARMADOLAR', 'Arma Dólar (Ahorro Programado)', 5.00, 50.00, 180, TRUE);

/* B. Creamos 2 Clientes de prueba */
INSERT INTO PERSONA_NATURAL (CEDULA, CELULAR, CORREO, PATRIMONIO, NOMBRE, APELLIDO, FECHA_NACIMIENTO, GENERO, ESTADO_CIVIL, OCUPACION, NACIONALIDAD) VALUES
('1710000001', '0999999991', 'juan@mail.com', 5000, 'Juan', 'Perez', '1990-01-01', 'M', 'SOLTERO', 'DEV', 'EC'),
('1710000002', '0999999992', 'maria@mail.com', 10000, 'Maria', 'Gomez', '1995-05-05', 'F', 'CASADA', 'DOCENTE', 'EC');

/* C. Les damos dinero en cuentas para probar */
INSERT INTO CUENTA_AHORROS (ID_CLIENTE, N_CUENTA, ESTADO, SALDO_ACTUAL) VALUES
(1, '2200001', 'ACTIVA', 1500.00), -- Juan tiene $1500
(2, '2200002', 'ACTIVA', 5000.00); -- Maria tiene $5000

INSERT INTO CUENTA_CORRIENTE (ID_CLIENTE, N_CUENTA, ESTADO, SALDO_ACTUAL) VALUES
(1, '4400001', 'ACTIVA', 200.00); -- Juan tiene $200 extras en corriente
