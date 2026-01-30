/* ================================================================ */
/* AGREGAR PRODUCTO: PAGO ANTICIPADO                                */
/* ================================================================ */

-- Este producto tiene intereses ANTICIPADOS (se pagan inmediatamente)
-- Restricciones:
-- - Monto mínimo: $500
-- - Plazo mínimo: 30 días
-- - Plazo máximo: 179 días
-- - Tasa: 6.00% anual

INSERT INTO INV_PRODUCTO (CODIGO, NOMBRE, TASA_ANUAL, MONTO_MIN, PLAZO_MIN_DIAS, ES_FLEXIBLE) VALUES 
('PAGOANTICIPADO', 'Inversión con Pago Anticipado', 6.00, 500.00, 30, FALSE);

-- Verificar que se insertó correctamente
SELECT * FROM INV_PRODUCTO WHERE CODIGO = 'PAGOANTICIPADO';
