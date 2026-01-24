/* ================================================================ */
/* VISTA AUXILIAR: UNIFICA EL ORIGEN DE FONDOS (SOLO LECTURA)      */
/* Esto permite a tu Python ver todas las cuentas como una sola    */
/* ================================================================ */

CREATE OR REPLACE VIEW V_INV_CUENTAS_CLIENTE AS
SELECT 
    'AHORRO' AS TIPO_ORIGEN,
    ID_CUENTA AS ID_INTERNO,
    N_CUENTA AS NUMERO_CUENTA,
    ID AS ID_CLIENTE, -- ID de la Persona (FK)
    SALDO_ACTUAL
FROM CUENTA_AHORROS
UNION ALL
SELECT 
    'CORRIENTE' AS TIPO_ORIGEN,
    ID_CUENTA AS ID_INTERNO,
    N_CUENTA AS NUMERO_CUENTA,
    ID AS ID_CLIENTE,
    SALDO_ACTUAL
FROM CUENTA_CORRIENTE;

/* ================================================================ */
/* TABLAS DEL MODULO DE INVERSIONES (PREFIJO INV_)                 */
/* ================================================================ */

/* 1. PRODUCTOS DE INVERSION (PlazoDolar, ArmaDolar, etc.) */
CREATE TABLE INV_PRODUCTO (
    ID_PRODUCTO     SERIAL PRIMARY KEY,
    CODIGO          VARCHAR(20) NOT NULL UNIQUE, -- 'PLAZO_FIJO', 'ARMA_DOLAR'
    NOMBRE          VARCHAR(50) NOT NULL,
    TASA_ANUAL      DECIMAL(5,2) NOT NULL, -- Tasa base referencial
    MONTO_MIN       DECIMAL(12,2) NOT NULL,
    PLAZO_MIN_DIAS  INT NOT NULL,
    ES_FLEXIBLE     BOOLEAN DEFAULT FALSE -- TRUE para ArmaDolar (permite abonos)
);

/* Insertamos tus submodulos como configuración */
INSERT INTO INV_PRODUCTO (CODIGO, NOMBRE, TASA_ANUAL, MONTO_MIN, PLAZO_MIN_DIAS, ES_FLEXIBLE) VALUES 
('PLAZODOLAR', 'Inversión Plazo Dólar', 6.50, 500.00, 30, FALSE),
('ARMADOLAR', 'Ahorro Programado ArmaDólar', 5.00, 50.00, 180, TRUE);


/* 2. LA INVERSIÓN CONCRETA DEL CLIENTE */
CREATE TABLE INV_SOLICITUD (
    ID_INVERSION    SERIAL PRIMARY KEY,
    ID_CLIENTE      INT NOT NULL,          -- Viene de PERSONA_NATURAL/JURIDICA
    ID_PRODUCTO     INT REFERENCES INV_PRODUCTO(ID_PRODUCTO),
    
    -- Datos para rastrear de dónde salió el dinero (usando la lógica de la VISTA)
    ORIGEN_FONDOS   VARCHAR(20) NOT NULL,  -- 'AHORRO' o 'CORRIENTE'
    ID_CUENTA_ORIGEN INT NOT NULL,         -- ID_CUENTA de la tabla original
    
    MONTO_CAPITAL   DECIMAL(12,2) NOT NULL,
    FECHA_INICIO    DATE DEFAULT CURRENT_DATE,
    FECHA_FIN       DATE NOT NULL,
    ESTADO          VARCHAR(20) DEFAULT 'ACTIVA', -- 'ACTIVA', 'PAGADA', 'CANCELADA'
    
    -- Cálculos guardados para no recalcular siempre
    INTERES_GANADO  DECIMAL(12,2) DEFAULT 0,
    TOTAL_A_RECIBIR DECIMAL(12,2) DEFAULT 0
);


/* 3. TU TABLA DE MOVIMIENTOS (El reemplazo temporal de Transacciones) */
/* Aquí registras: "Salieron $500 de Ahorros para entrar a Inversión #1" */
CREATE TABLE INV_MOVIMIENTO_FINANCIERO (
    ID_MOVIMIENTO   SERIAL PRIMARY KEY,
    ID_INVERSION    INT REFERENCES INV_SOLICITUD(ID_INVERSION),
    
    TIPO_MOV        VARCHAR(20) NOT NULL, -- 'DEBITO_APERTURA', 'ABONO_EXTRA', 'PAGO_INTERES', 'RETORNO_CAPITAL'
    MONTO           DECIMAL(12,2) NOT NULL,
    FECHA_REGISTRO  TIMESTAMP DEFAULT NOW(),
    
    DESCRIPCION     VARCHAR(200)
);

/* 4. TABLA PARA "PAGO ANTICIPADO" (Tu tercer submódulo) */
/* Si alguien cancela antes, registras la penalización aquí */
CREATE TABLE INV_PENALIZACION (
    ID_PENALIDAD    SERIAL PRIMARY KEY,
    ID_INVERSION    INT REFERENCES INV_SOLICITUD(ID_INVERSION),
    MONTO_MULTA     DECIMAL(12,2) NOT NULL,
    MOTIVO          VARCHAR(100) DEFAULT 'CANCELACION_ANTICIPADA',
    FECHA           DATE DEFAULT CURRENT_DATE
);

# servicio_inversiones.py

def crear_plazodolar(id_cliente, monto, id_cuenta_origen, tipo_cuenta):
    
    # 1. VERIFICAR FONDOS (Usando tu VISTA, no las tablas crudas)
    # SQL: SELECT saldo_actual FROM V_INV_CUENTAS_CLIENTE WHERE id_interno = ? AND tipo = ?
    saldo = db.query_vista_cuentas(id_cuenta_origen, tipo_cuenta)
    
    if saldo < monto:
        return "Error: Fondos insuficientes"

    # 2. "CONGELAR" EL DINERO (Simulado)
    # Como no puedes hacer UPDATE fiable a las tablas de ellos porque son un caos,
    # asume que el dinero está tomado.
    # Opcional: Si te atreves, haz el UPDATE directo:
    if tipo_cuenta == 'AHORRO':
        db.execute("UPDATE CUENTA_AHORROS SET SALDO_ACTUAL = SALDO_ACTUAL - ? WHERE ...", monto)
    else:
        db.execute("UPDATE CUENTA_CORRIENTE SET SALDO_ACTUAL = SALDO_ACTUAL - ? WHERE ...", monto)

    # 3. CREAR LA INVERSION (En tus tablas propias)
    id_inv = db.insert_inv_solicitud(...)
    
    # 4. REGISTRAR EL MOVIMIENTO (En tu tabla propia, no en TRANSACCIONES)
    db.insert_inv_movimiento(id_inv, 'DEBITO_APERTURA', monto)

    return "Inversión creada con éxito"

    