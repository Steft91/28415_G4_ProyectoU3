# src/controllers/inversiones.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models.database import get_cuentas_usuario, get_producto_info, procesar_inversion, simular_paso_tiempo
inversiones = Blueprint('inversiones', __name__)

@inversiones.route('/plazo-dolar', methods=['GET', 'POST'])
@login_required
def plazodolar():
    info_producto = get_producto_info('PLAZODOLAR')
    
    if request.method == 'POST':
        try:
            monto = request.form.get('monto')
            tiempo_input = request.form.get('dias')  # El número que escribe el usuario (ej: 60 o 2)
            tipo_plazo = request.form.get('tipo_plazo') # 'dias' o 'meses' (radio button)
            cuenta_id = request.form.get('cuenta_id')
            
            # --- LÓGICA DE DÍAS VS MESES ---
            dias_totales = int(tiempo_input)
            
            # Si eligió meses, multiplicamos por 30 (estándar bancario simple)
            if tipo_plazo == 'meses':
                dias_totales = dias_totales * 30
            
            # Enviamos a la BD el total de días ya calculado
            exito, mensaje = procesar_inversion(
                id_usuario=current_user.id,
                id_cuenta=cuenta_id,
                monto=monto,
                dias=dias_totales, 
                tasa=info_producto['tasa']
            )
            
            if exito:
                flash("¡Inversión realizada con éxito! Revisa tu Dashboard.", "success")
                return redirect(url_for('dashboard'))
            else:
                flash(f"Error al invertir: {mensaje}", "danger")
        
        except Exception as e:
            flash(f"Error inesperado: {e}", "danger")

    cuentas = get_cuentas_usuario(current_user.id)
    if not info_producto:
        return redirect(url_for('dashboard'))

    return render_template('inversiones/plazodolar.html', p=info_producto, cuentas=cuentas)

# --- NUEVA RUTA PARA EL SIMULADOR DE TIEMPO ---
@inversiones.route('/simular-avance', methods=['POST'])
@login_required
def simular_avance():
    id_inversion = request.form.get('id_inversion')
    fecha_simulada = request.form.get('fecha_simulada')
    
    exito, mensaje = simular_paso_tiempo(id_inversion, fecha_simulada)
    
    if exito:
        flash(mensaje, "success")
    else:
        # Usamos 'info' si es solo aviso de tiempo, 'danger' si es error real
        if "Aún no vence" in mensaje:
            flash(mensaje, "warning")
        else:
            flash(mensaje, "danger")
            
    return redirect(url_for('dashboard'))

# RUTA ARMADOLAR (Placeholder)
@inversiones.route('/armadolar')
@login_required
def armadolar():
    return render_template('dashboard.html')