# src/controllers/inversiones.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models.database import get_cuentas_usuario, get_producto_info, procesar_inversion, simular_paso_tiempo, procesar_pago_anticipado
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
@inversiones.route('/armadolar', methods=['GET', 'POST'])
@login_required
def armadolar():
    info_producto = get_producto_info('ARMADOLAR')

    if request.method == 'POST':
        try:
            monto = float(request.form.get('monto'))
            dias = int(request.form.get('dias'))
            frecuencia = int(request.form.get('frecuencia'))
            cuenta_id = request.form.get('cuenta_id')

            # 🔒 Validaciones Armadolar
            if monto < 500:
                flash("El monto mínimo es $500", "danger")
                return redirect(url_for('inversiones.armadolar'))

            if dias < 90:
                flash("El plazo mínimo es 90 días", "danger")
                return redirect(url_for('inversiones.armadolar'))

            exito, mensaje = procesar_inversion(
                id_usuario=current_user.id,
                id_cuenta=cuenta_id,
                monto=monto,
                dias=dias,
                tasa=info_producto['tasa'],
                frecuencia_pago=frecuencia   # 👈 SOLO ARMADOLAR USA ESTO
            )

            if exito:
                flash("¡Tu Armadolar fue creado exitosamente!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash(mensaje, "danger")

        except Exception as e:
            flash(f"Error inesperado: {e}", "danger")

    cuentas = get_cuentas_usuario(current_user.id)

    if not info_producto:
        flash("Producto Armadolar no disponible", "danger")
        return redirect(url_for('dashboard'))

    return render_template(
        'inversiones/armadolar.html',
        p=info_producto,
        cuentas=cuentas
    )

# RUTA PAGO ANTICIPADO
@inversiones.route('/pago-anticipado', methods=['GET', 'POST'])
@login_required
def pago_anticipado():
    info_producto = get_producto_info('PAGOANTICIPADO')
    
    if request.method == 'POST':
        try:
            monto = float(request.form.get('monto'))
            dias = int(request.form.get('dias'))
            cuenta_id = request.form.get('cuenta_id')

            # Validaciones específicas de Pago Anticipado
            if monto < 500:
                flash("El monto mínimo es $500", "danger")
                return redirect(url_for('inversiones.pago_anticipado'))

            if dias < 30:
                flash("El plazo mínimo es 30 días", "danger")
                return redirect(url_for('inversiones.pago_anticipado'))
            
            if dias > 179:
                flash("El plazo máximo es 179 días", "danger")
                return redirect(url_for('inversiones.pago_anticipado'))

            # Procesar con la función especial de pago anticipado
            exito, mensaje = procesar_pago_anticipado(
                id_usuario=current_user.id,
                id_cuenta=cuenta_id,
                monto=monto,
                dias=dias,
                tasa=info_producto['tasa']
            )

            if exito:
                flash(mensaje, "success")
                return redirect(url_for('dashboard'))
            else:
                flash(f"Error al invertir: {mensaje}", "danger")

        except Exception as e:
            flash(f"Error inesperado: {e}", "danger")

    cuentas = get_cuentas_usuario(current_user.id)

    if not info_producto:
        flash("Producto Pago Anticipado no disponible", "danger")
        return redirect(url_for('dashboard'))

    return render_template(
        'inversiones/retiro_anticipado.html',
        p=info_producto,
        cuentas=cuentas
    )
