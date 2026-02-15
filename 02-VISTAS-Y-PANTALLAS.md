# 02 - VISTAS Y PANTALLAS DEL NUEVO CRM PROTEGRT WEB

> Documento generado a partir del analisis exhaustivo de TODAS las vistas, dialogos y componentes del sistema actual (PyQt5).
> Para cada pantalla se documenta: que muestra, datos del backend, acciones del usuario, mejoras propuestas y layout web.
> Incluye vistas nuevas propuestas y apps moviles.

---

## INDICE

1. [Autenticacion](#1-autenticacion)
2. [Dashboard Principal](#2-dashboard-principal)
   - Dashboard General (Principal)
   - Dashboard de Cobranza
   - Dashboards de Otras Areas
3. [Modulo Clientes](#3-modulo-clientes)
4. [Modulo Polizas](#4-modulo-polizas)
5. [Modulo Cobranza](#5-modulo-cobranza)
   - Dashboard de Cobranza
   - Pagos
   - Pagos Temporales (Pendientes de Autorizacion) -- UNIFICADO con Panel Autorizacion de Pagos (10.2)
   - Revision de Pagos -- UNIFICADO con Pendientes de Autorizacion
   - Tarjetas (Cuentas de Cobranza) -- REDISENO con 3 propuestas
   - Recibos (fisicos + electronicos)
   - Cancelaciones
   - Contado a Cuotas -- INTEGRADO como pestana en Pagos
   - Promociones
   - Mensajes de Cobranza
   - Avisos de Visita y Tracking de Rutas -- AMPLIADO
   - Cobradores
6. [Modulo Siniestros](#6-modulo-siniestros)
7. [Modulo Gruas](#7-modulo-gruas)
8. [Modulo Endosos](#8-modulo-endosos)
9. [Modulo Administracion](#9-modulo-administracion)
   - Empleados (unifica Vendedores, Cobradores, Ajustadores)
   - Coberturas
   - Guardias de Ajustadores
   - Renovaciones
   - Proveedores de Gruas
   - Usuarios
10. [Vistas Nuevas Propuestas](#10-vistas-nuevas-propuestas)
11. [Apps Moviles](#11-apps-moviles)
12. [Navegacion Global y Layout](#12-navegacion-global-y-layout)

---

## 1. AUTENTICACION

### 1.1 Pantalla de Login

**Vista actual**: `views/login_view.py`

**Que muestra**:
- Logo de la empresa
- Campo de usuario
- Campo de contrasena (con toggle mostrar/ocultar)
- Boton de iniciar sesion
- Enlace "Olvidaste tu contrasena?"

> **ELIMINADO:** "Recordar usuario/contrasena" -- multiples personas usan las mismas PCs en la oficina,
> no se debe guardar credenciales en el navegador.
>
> **ELIMINADO:** "Acceder sin cuenta" -- TODO acceso al sistema requiere autenticacion completa.

**Datos del backend**:
- `POST /api/v1/auth/login` -> { username, password } -> { access_token, refresh_token, user }

**Acciones del usuario**:
- Iniciar sesion con credenciales
- Recuperar contrasena olvidada

**Mejoras para web**:
- Agregar autenticacion de dos factores (2FA) opcional (obligatorio para admin y gerente)
- Pantalla de "Olvidaste tu contrasena" con reset por email
- Login responsivo: centrado vertical/horizontal, degradado de fondo con branding
- Soporte para OAuth2 futuro (Google Workspace de la empresa)

**Layout web**:
```
+--------------------------------------------------+
|                                                    |
|            +----------------------------+          |
|            |        [LOGO]              |          |
|            |                            |          |
|            |  Usuario:                  |          |
|            |  [____________________]    |          |
|            |                            |          |
|            |  Contrasena:               |          |
|            |  [____________________] [o]|          |
|            |                            |          |
|            |  [  INICIAR SESION  ]      |          |
|            |                            |          |
|            |  Olvidaste tu contrasena?  |          |
|            +----------------------------+          |
|                                                    |
+--------------------------------------------------+
```

**Endpoints**:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`

### 1.2 Dialogo de Cambio de Contrasena

**Vista actual**: `views/change_password_dialog.py`

**Que muestra**: Formulario con contrasena actual, nueva contrasena, confirmar nueva contrasena.

**En web**: Modal accesible desde el menu de perfil del usuario. Validacion de fortaleza en tiempo real.

**Endpoint**: `PUT /api/v1/auth/me/password`

---

## 2. DASHBOARD PRINCIPAL

> **REDISENO:** El sistema tendra un dashboard por cada area de negocio + un dashboard principal general.
> Cada departamento tiene metricas especificas que le importan. El dashboard principal es un resumen ejecutivo.

### 2.1 Dashboard General (Principal)

**Vista actual**: `views/dashboard_view.py`

**Proposito**: Resumen ejecutivo del estado general del negocio. Visible para todos los roles.

**Que muestra**:
- Tarjeta de siniestros abiertos (con contador y status)
- Tarjeta de gruas abiertas/activas
- Widget de alertas criticas:
  - Grua con tiempo de arribo vencido sin reporte del proveedor
  - Ajustador con tiempo de llegada vencido sin reporte
  - Polizas contado-a-cuotas con segundo pago vencido
  - Pagos pendientes de autorizacion >48 horas sin revisar
- Widget de actividad reciente (ultimas polizas creadas, pagos registrados, siniestros reportados)
- Graficas interactivas con drill-down (click en barra -> ver detalle)
- Filtro por rango de fechas
- Filtro por vendedor (gerentes ven todo, vendedores solo lo suyo)
- Widgets configurables (drag & drop para reordenar)
- Auto-refresco cada 5 minutos

> **ALERTAS AUTOMATICAS:** El sistema debe generar notificaciones de alerta automatica cuando:
> - Se cumple el tiempo estimado de arribo de una grua sin que el proveedor haya reportado llegada
> - Un ajustador tarda mas del tiempo esperado en llegar al siniestro sin reportar status
> - Situaciones similares donde un evento esperado no ocurre dentro del tiempo configurado
> Estas alertas aparecen en el dashboard principal y se envian por push/WebSocket a los responsables.

**Layout web**:
```
+-------+---------------------------------------------+
| MENU  |  Dashboard General                  [Perfil] |
| LAT.  |                                              |
|       |  +----------+ +----------+ +----------+      |
| Dash  |  |Siniestros| | Gruas    | | Alertas  |      |
| Clien |  | abiertos | | activas  | | criticas |      |
| Poliz |  |    5     | |    2     | |    3     |      |
| Cobr  |  +----------+ +----------+ +----------+      |
| Sinie |                                              |
| Gruas |  +-------------------------------------------+|
| RRHH  |  | ALERTAS                                   ||
| Admin |  | [!] Grua F:18501 - 45min sin reporte      ||
|       |  | [!] Ajustador M02 - 30min sin llegada     ||
|       |  | [!] 3 pagos >48h sin revisar              ||
|       |  +-------------------------------------------+|
|       |                                              |
|       |  +--------------------+ +------------------+ |
|       |  | Actividad reciente | | Polizas/Mes(bar) | |
|       |  | - Poliza 18510     | |                  | |
|       |  | - Pago F:18405     | |                  | |
|       |  | - Siniestro #234   | |                  | |
|       |  +--------------------+ +------------------+ |
|       |                                              |
|       |  +--------------------+ +------------------+ |
|       |  | Coberturas (pie)   | | Tipos vehic.(pie)| |
|       |  |                    | |                  | |
|       |  +--------------------+ +------------------+ |
+-------+---------------------------------------------+
```

### 2.2 Dashboard de Cobranza

**Proposito**: Metricas especificas del area de cobranza. Visible para gerente de cobranza, admin, y auxiliares de cobranza.

**Que muestra**:
- Tarjeta de ingresos del dia / mes / ano (montos cobrados)
- Tarjeta de polizas morosas con porcentaje sobre total de polizas activas
- Tarjeta de pagos pendientes de autorizacion
- Graficas de tendencia de cobranza
- Eficiencia por cobrador
- Comparativo mes actual vs mes anterior
- Mapa de calor por zona de cobranza (PostGIS)

> **Nota:** Las metricas detalladas de cobranza se documentan en la seccion 5.1 (Dashboard de Cobranza del modulo).

### 2.3 Dashboards de Otras Areas

Cada area tendra su propio dashboard con metricas relevantes:

- **Dashboard de Ventas**: polizas del dia/mes/ano, meta vs real por vendedor, renovaciones pendientes, comisiones
- **Dashboard de Siniestros**: siniestros abiertos por status, tiempo promedio de respuesta, ajustadores en campo, encuestas de satisfaccion
- **Dashboard de RRHH**: empleados activos, solicitudes de vacaciones pendientes, permisos del mes

**Endpoints**:
- `GET /api/v1/dashboard/general?from=2026-01-01&to=2026-02-14`
- `GET /api/v1/dashboard/cobranza?from=&to=`
- `GET /api/v1/dashboard/ventas?from=&to=&vendedor_id=`
- `GET /api/v1/dashboard/siniestros?from=&to=`
- `GET /api/v1/dashboard/alerts`
- `GET /api/v1/dashboard/activity?limit=10`

---

## 3. MODULO CLIENTES

### 3.1 Listado de Clientes

**Vista actual**: `views/clientes_view.py`

**Que muestra**:
- Titulo "Clientes"
- Barra de busqueda (por nombre, telefono, email)
- Boton "+ Agregar Cliente"
- Boton "Actualizar"
- Tabla con columnas: ID, Nombre, Apellido Paterno, Apellido Materno, WhatsApp (numero principal), Numero Adicional, Email, Direccion, Municipio, Estado
- Paginacion (14 items por pagina)
- Doble clic en fila -> abre detalle del cliente

**Datos del backend**:
- `GET /api/v1/clients?page=1&per_page=14&search=Juan`

**Acciones del usuario**:
- Buscar clientes por nombre/telefono/email
- Agregar nuevo cliente (abre formulario)
- Ver detalle de cliente (doble clic)
- Editar cliente
- Ver polizas del cliente
- Actualizar lista

**Mejoras para web**:
- Busqueda avanzada con multiples filtros (estado, municipio, tiene poliza activa)
- Vista de mapa con ubicacion de clientes (PostGIS)
- Indicador visual de clientes con polizas morosas/activas/canceladas
- Columna de "status" del cliente (activo/moroso/sin polizas)
- Acciones rapidas en cada fila (ver polizas, llamar, enviar WhatsApp)
- Al crear cliente nuevo: enviar WhatsApp de verificacion para confirmar que el numero es correcto (recomendado pero no obligatorio)

> **ELIMINADO:** Exportar a Excel/CSV. No queremos que los empleados puedan sacar informacion
> de clientes facilmente. Los datos de clientes se consultan dentro del sistema pero no se exportan.

**Layout web**:
```
+-------+---------------------------------------------+
| MENU  |  Clientes                     [+ Agregar]    |
|       |                                              |
|       |  [Buscar...________] [Estado v] [Municipio v]|
|       |                                              |
|       |  +------------------------------------------+|
|       |  | ID | Nombre    | WhatsApp | Email | ... ||
|       |  |----|-----------|----------|-------|-----||
|       |  | 1  | Juan Pz   | 33-1234  | j@..  | ...||
|       |  | 2  | Maria Lg  | 33-5678  | m@..  | ...||
|       |  +------------------------------------------+|
|       |                                              |
|       |  [< 1 2 3 ... 50 >]    Mostrando 1-14 de 700|
+-------+---------------------------------------------+
```

**Endpoints**:
- `GET /api/v1/clients?page=1&per_page=20&search=&state=&municipality=`
- `POST /api/v1/clients`
- `GET /api/v1/clients/:id`
- `PUT /api/v1/clients/:id`
- `GET /api/v1/clients/:id/policies`
- `POST /api/v1/clients/:id/verify-whatsapp` (enviar mensaje de verificacion de numero)

### 3.2 Formulario de Cliente (Crear/Editar)

**Dialogos actuales**: `views/dialogs/clientes/cliente_dialog.py`, `cliente_form_dialog.py`

**Que muestra**: Formulario con campos: nombre, apellido paterno, apellido materno, WhatsApp (numero principal de WhatsApp), numero adicional, email, calle, numero exterior, numero interior, colonia, municipio (con busqueda), estado, codigo postal, RFC.

**Datos del backend**:
- `GET /api/v1/catalogs/municipalities` (para autocompletar municipio)
- `GET /api/v1/catalogs/states`

**Acciones**: Guardar, cancelar, validar campos obligatorios.

**Mejoras para web**:
- Autocompletar municipio y colonia a partir de codigo postal (API SEPOMEX)
- Validacion de RFC en tiempo real (formato correcto)
- Validacion de telefono (10 digitos, formato mexicano)
- Al guardar con numero de WhatsApp: opcion de enviar mensaje de verificacion para confirmar que el numero es correcto (recomendado pero no obligatorio, el usuario puede omitir la verificacion)
- Geocodificacion automatica de direccion para PostGIS
- Deteccion de clientes duplicados (nombre + telefono similar)
- En web: modal deslizable desde la derecha (drawer) en lugar de dialog

**Layout web**: Formulario en 2 columnas dentro de un drawer lateral.

### 3.3 Detalle de Cliente

**Dialogo actual**: `views/dialogs/clientes/cliente_dialog.py`

**Que muestra**: Informacion del cliente + lista de polizas asociadas.

**Mejoras para web**:
- Panel lateral con datos del cliente
- Tabs: Polizas | Pagos | Siniestros | Mensajes | Historial
- Timeline de actividad del cliente
- Boton de "Llamar" (integracion telefonia VoIP futura)
- Boton "Enviar WhatsApp" (usa el numero de WhatsApp verificado del cliente)

### 3.4 Buscar Cliente (Selector)

**Dialogo actual**: `views/dialogs/clientes/buscar_cliente_dialog.py`, `buscar_cliente_poliza_dialog.py`

**Que muestra**: Campo de busqueda + tabla de resultados para seleccionar un cliente (usado al crear poliza).

**En web**: Componente de autocompletar con preview (typeahead search). Al escribir 3+ caracteres muestra lista desplegable con clientes coincidentes.

---

## 4. MODULO POLIZAS

### 4.1 Listado de Polizas

**Vista actual**: `views/polizas_view.py`

**Que muestra**:
- Titulo "Polizas"
- Busqueda por folio o placas
- Filtro por vendedor (combo box)
- Boton "Agregar Poliza"
- Tabla con columnas: Folio, Folio Contrato, Cliente, Cobertura, Servicio, Tipo Vehiculo, Marca, Modelo, Ano, Placas, Vigencia, Fin Vigencia, Forma Pago, Prima Total, Vendedor, Status
- Paginacion (24 items)
- Colores por status (verde=Activa, amarillo=Pendiente, naranja=Morosa, rojo=Cancelada, gris=Expirada)
- Clic derecho: menu contextual con acciones rapidas (ver pagos, editar, imprimir, renovar, etc.)
- Filtro visual por badges (se muestran filtros activos como chips)

**Datos del backend**:
- `GET /api/v1/policies?page=1&per_page=24&search=&vendedor_id=&status=`

**Acciones del usuario**:
- Buscar polizas
- Filtrar por vendedor
- Filtrar por status
- Crear nueva poliza
- Ver detalle de poliza (doble clic)
- Editar poliza (menu contextual)
- Ver pagos de la poliza
- Imprimir contrato
- Renovar poliza
- Cambiar vendedor
- Ver endosos

**Mejoras para web**:
- Filtros avanzados: por status, cobertura, tipo vehiculo, rango de fechas, vendedor
- Busqueda global (folio, placas, nombre cliente, serie)
- Vista de tabla con columnas configurables (mostrar/ocultar)
- Exportar a Excel
- Acciones en lote (seleccionar multiples polizas y operar)
- Indicador visual de servicios de grua disponibles
- Mini preview al pasar mouse sobre una fila

**Layout web**:
```
+-------+---------------------------------------------+
| MENU  |  Polizas                     [+ Nueva Poliza]|
|       |                                              |
|       |  [Buscar folio/placas...] [Vendedor v]       |
|       |  [Status v] [Cobertura v] [Tipo Vehiculo v]  |
|       |  Filtros activos: [AMPLIA x] [Activa x]      |
|       |                                              |
|       |  +------------------------------------------+|
|       |  | Folio | Cliente | Cobert. | Status | ... ||
|       |  |-------|---------|---------|--------|-----||
|       |  | 18501 | Juan P  | AMPLIA  | Activa | ...||
|       |  | 18502 | Maria L | PLATINO | Morosa | ...||
|       |  +------------------------------------------+|
|       |                                              |
|       |  [< 1 2 3 ... >]        Total: 5,230 polizas|
+-------+---------------------------------------------+
```

**Endpoints**:
- `GET /api/v1/policies?page=1&per_page=24&search=&vendedor_id=&status=&cobertura=&tipo_vehiculo=&fecha_desde=&fecha_hasta=`
- `POST /api/v1/policies`
- `GET /api/v1/policies/:folio`
- `PUT /api/v1/policies/:folio`
- `PUT /api/v1/policies/:folio/vendedor`
- `POST /api/v1/policies/:folio/renew`
- `GET /api/v1/policies/export?format=xlsx`

### 4.2 Formulario de Poliza (Crear/Editar/Renovar)

**Dialogo actual**: `views/dialogs/polizas/poliza_form_dialog.py` + sub-widgets

**Que muestra**: Formulario con 3 tabs:
1. **Info de Poliza**: Folio (auto), folio contrato, cobertura (combo), servicio (combo), forma de pago (combo), vendedor (combo), vigencia (date), fin vigencia (auto), prima total, imagen del contrato, numero de cotizacion
2. **Info del Vehiculo**: Tipo (combo), marca, modelo (ano), color, serie (VIN), placas, motor
3. **Info del Cliente**: Buscador de cliente existente o formulario para crear nuevo

**Subcomponentes**:
- `poliza_info_widget.py`: Campos de poliza
- `vehiculo_info_widget.py`: Campos del vehiculo
- `cliente_info_widget.py`: Buscador/formulario de cliente

**Datos del backend**:
- `GET /api/v1/catalogs/coverages`
- `GET /api/v1/catalogs/vehicle-types`
- `GET /api/v1/sellers?status=active`
- `GET /api/v1/quotes/validate/:quote_number` (para AMPLIA)
- `POST /api/v1/policies`

**Acciones**: Buscar cliente, seleccionar cobertura (actualiza precios), validar cotizacion AMPLIA, subir imagen del contrato, guardar.

**Mejoras para web**:
- Wizard (paso a paso) en lugar de tabs: Paso 1: Cliente -> Paso 2: Vehiculo -> Paso 3: Cobertura y Pagos -> Paso 4: Confirmar
- Autocompletar marca y modelo del vehiculo (catalogo AMIS)
- Escaneo de VIN para autocompletar datos del vehiculo
- Upload drag & drop de imagen del contrato
- Preview del contrato subido
- Calculo automatico de prima en tiempo real
- Validacion de AMPLIA SELECT con indicador visual de elegibilidad
- Resumen de costos antes de confirmar

**Layout web**: Wizard de 4 pasos, pantalla completa.

### 4.3 Detalle de Poliza

**Dialogo actual**: `views/dialogs/polizas/poliza_details_dialog.py`

**Que muestra**:
- Datos del cliente (nombre, direccion, telefonos)
- Datos del vehiculo (marca, modelo, ano, placas, serie)
- Datos de la poliza (folio, cobertura, vigencia, status, vendedor, prima)
- Imagen del contrato (carga asincrona desde servidor de archivos)
- Boton para ver elegibilidad AMPLIA SELECT
- Boton para editar poliza

**Mejoras para web**:
- Pagina completa de detalle (URL: `/polizas/:folio`)
- Sidebar con datos resumidos, area principal con tabs
- Tabs: Informacion | Pagos | Endosos | Siniestros | Gruas | Historial
- Imagen del contrato con visor integrado (zoom, rotacion)
- Timeline de eventos de la poliza
- Acciones contextuales en header (editar, renovar, cancelar, imprimir)

### 4.4 Dialogo de Pagos de Poliza

**Dialogo actual**: `views/dialogs/polizas/poliza_pagos_dialog.py`

**Que muestra**:
- Resumen de la poliza (folio, cobertura, prima, forma pago)
- Monto total pagado vs monto pendiente
- Tabla de todos los pagos con status visual (iconos de color)
- Botones: agregar pago, editar pago, problema de pago (AMPLIA SELECT), abono parcial

**En web**: Tab "Pagos" dentro del detalle de poliza, con las mismas funcionalidades.

### 4.5 Formulario de Pago (Crear/Editar)

**Dialogo actual**: `views/dialogs/polizas/poliza_pago_form_dialog.py`

**Que muestra**: Formulario con: numero de recibo, fecha limite, fecha real, monto, metodo de pago, cobrador, status, entregado en oficina, fecha entrega, comentarios.

**Validaciones**: Recibo verificado, fechas coherentes, status correcto segun fecha.

**En web**: Modal con formulario validado. Verificacion de recibo via API en tiempo real.

### 4.6 Dialogo de Reestructurar Pagos (Contado a Cuotas)

**Dialogo actual**: `views/dialogs/polizas/restructurar_pagos_dialog.py`

**Que muestra**: Resumen de la poliza, pagos actuales, preview de pagos reestructurados, boton confirmar.

**En web**: Modal con preview comparativo (antes vs despues).

### 4.7 Elegibilidad AMPLIA SELECT

**Dialogo actual**: `views/dialogs/polizas/amplia_select_eligibility_dialog.py`

**Que muestra**: 4 criterios de elegibilidad (sin problemas de pago, sin siniestros, historial de renovacion, cliente anterior) con indicadores de cumplimiento (check/X).

**En web**: Panel dentro del detalle de poliza, con indicadores visuales claros.

---

## 5. MODULO COBRANZA

### 5.1 Dashboard de Cobranza

**Vista actual**: `views/cobranza_dashboard_view.py`

> **Este es el dashboard especifico del area de cobranza** (ver seccion 2.2 para el dashboard general).

**Que muestra**:
- Header "Dashboard de Cobranza" con boton de actualizar
- Tarjetas de metricas: Ingresos del dia / mes / ano, Total polizas, Total recaudado, Pendiente por cobrar, Polizas morosas con porcentaje sobre total
- Seccion de cobradores: tabla con nombre, tarjetas asignadas, cobros del mes, monto cobrado
- Seccion de pagos: resumen por metodo de pago, pagos del dia
- Seccion de resumen: grafica de cobros por periodo
- Alerta de folios sin pagos (discrepancias)

**Datos del backend**:
- `GET /api/v1/collections/dashboard`

**Acciones**: Ver metricas, ver detalle por cobrador, detectar discrepancias.

**Mejoras para web**:
- Graficas interactivas de tendencia de cobranza
- Mapa de calor por zona de cobranza (PostGIS)
- Indicador de eficiencia por cobrador (% cobrado vs asignado)
- Comparativo mes actual vs mes anterior
- Drill-down: click en cobrador -> ver sus tarjetas y pagos
- Widget de "Polizas criticas" (vencidas >30 dias)

**Layout web**:
```
+-------+---------------------------------------------+
| MENU  |  Dashboard de Cobranza           [Actualizar]|
|       |                                              |
|       |  +--------+ +--------+ +--------+ +--------+|
|       |  | Total  | |Recaudad| |Pendient| | Morosas||
|       |  | 1,250  | |$450K   | |$280K   | |  230   ||
|       |  +--------+ +--------+ +--------+ +--------+|
|       |                                              |
|       |  +-------------------+ +-------------------+ |
|       |  | Cobros x Cobrador | | Cobros x Metodo   | |
|       |  |  (tabla)          | |  (grafica)        | |
|       |  +-------------------+ +-------------------+ |
|       |                                              |
|       |  +-------------------------------------------+|
|       |  | Tendencia de Cobranza (linea temporal)    ||
|       |  +-------------------------------------------+|
+-------+---------------------------------------------+
```

**Endpoints**:
- `GET /api/v1/collections/dashboard`
- `GET /api/v1/collections/dashboard/by-collector`
- `GET /api/v1/collections/dashboard/by-method`
- `GET /api/v1/collections/dashboard/trend?months=6`
- `GET /api/v1/collections/discrepancies`

### 5.2 Pagos

**Vista actual**: `views/pagos_view.py`

**Que muestra**:
- Titulo "Pagos"
- Panel de informacion de poliza (recuadro azul con folio, cobertura, cliente, vigencia, status)
- Barra de busqueda por folio
- Tabla de pagos de la poliza: Numero Pago, Numero Recibo, Fecha Limite, Fecha Real, Monto, Metodo Pago, Cobrador, Status (con iconos), Entregado en Oficina, Comentarios
- Formulario de edicion de pago (lateral)
- Botones: Editar, Problema de Pago, Abono Parcial

**Datos del backend**:
- `GET /api/v1/policies/:folio/payments`
- `PUT /api/v1/payments/:id`

**Acciones**: Buscar por folio, editar pago, registrar abono parcial, marcar problema de pago.

**Mejoras para web**:
- Vista master-detail: lista de folios a la izquierda, pagos del folio seleccionado a la derecha
- Filtros rapidos de pagos: pendientes, atrasados, vencidos, pagados
- Timeline visual de pagos (barra de progreso con fechas)
- Acciones en lote (marcar varios pagos como pagados)
- Historial de cambios de cada pago (audit trail)

> **CONTROL DE ACCESO:** Solo el area de cobranza puede editar pagos. Todos los usuarios pueden
> VER la situacion de pagos de cualquier poliza, pero solo usuarios con permisos de cobranza
> pueden editar, eliminar o revertir pagos.
>
> **NOTA:** Se discutira a detalle mas adelante las reglas exactas de quien puede hacer que con los pagos.

### 5.3 Pagos Temporales (Pendientes de Autorizacion)

**Vista actual**: `views/pagos_temporales_view.py`

**Que muestra**:
- Titulo "Pagos Temporales"
- Panel de info de poliza
- Busqueda por folio
- Tabla de pagos temporales: mismas columnas que pagos + estado_pago (activo/aplicado/cancelado)
- Formulario de edicion
- Botones: Editar, Generar Reporte Excel

**Datos del backend**:
- `GET /api/v1/authorization/payments?folio=&status=active`

**Acciones**: Buscar, editar pago temporal, generar reporte diario.

**Mejoras para web**:
- Renombrar a "Pendientes de Autorizacion" (terminologia correcta del negocio)
- Vista de lista con filtros: todos, pendientes, aprobados, rechazados
- Panel lateral con preview del pago propuesto vs pago original
- Boton de "Aprobar" y "Rechazar" con campo de motivo
- Notificacion en tiempo real cuando llega una nueva propuesta (WebSocket)
- Badge con contador en el menu lateral
- Flujo de aprobacion por montos (>$5000 requiere gerente)
- Foto del recibo/baucher subida desde app movil

> **VISION: RECIBOS DIGITALES.** La idea de la app movil es ELIMINAR los recibos impresos fisicos.
> Todo el flujo debe ser digital: el cobrador registra el cobro en la app, se genera un recibo digital,
> y se envia al cliente por WhatsApp.
>
> - Si el cliente insiste en recibo fisico: el cobrador puede imprimir desde la app usando una
>   impresora portatil Bluetooth conectada al celular.
> - Se mantiene coexistencia con recibos impresos tradicionales para casos donde el cobrador
>   este fuera de cobertura de datos y no pueda usar la app.
> - El objetivo a mediano plazo es dejar de usar los recibos impresos actuales por completo.

### 5.4 Revision de Pagos

**Vista actual**: `views/revision_pagos_view.py`

**Que muestra**:
- Titulo "Revision de Pagos"
- Panel de info de poliza
- Busqueda por folio
- Tabla de pagos temporales (para revision)
- Tabla de pagos originales (referencia)
- Formulario de edicion con verificacion de recibo
- Al editar: sincroniza recibo, actualiza status, verifica liquidacion, notifica WhatsApp

**Datos del backend**:
- `GET /api/v1/authorization/payments?folio=`
- `POST /api/v1/authorization/payments/:id/apply`

**Acciones**: Revisar pagos temporales, verificar recibo, aplicar al pago original.

**Mejoras para web**:
- Unificar con "Pendientes de Autorizacion" en una sola pantalla con pestanas
- Vista de comparacion lado a lado: propuesta vs original
- Boton de "Aplicar" con confirmacion
- Log de quien reviso y cuando
- Alerta si el pago tiene mas de 48 horas sin revisar

### 5.5 Tarjetas (Cuentas de Cobranza)

**Vista actual**: `views/tarjetas_view.py`

**Que muestra**:
- Vista tipo "solitario" con columnas por cobrador
- Cada columna muestra las tarjetas asignadas a ese cobrador
- Cada tarjeta muestra: folio, nombre cliente, dias de atraso, saldo pendiente, status con color
- Drag & drop para reasignar tarjetas entre cobradores
- Barra de busqueda
- Filtro por cobrador
- Menu contextual (clic derecho): ver poliza, ver pagos, reasignar
- Columnas especiales: OFICINA, ARCHIVO, DEPOSITO

**Datos del backend**:
- `GET /api/v1/cards?grouped_by=location`
- `PUT /api/v1/cards/:id/reassign`

**Acciones**: Ver tarjetas por cobrador, reasignar (drag & drop o menu), buscar por folio/cliente, ver detalle.

**Mejoras para web**:

> **REDISENO COMPLETO.** La vista actual tipo "solitario" con columnas por cobrador necesita repensarse
> para web. Se proponen 3 alternativas de diseno. Se evaluara cual funciona mejor para el equipo.

#### Propuesta 1: Vista de Lista Inteligente con Agrupacion Dinamica

**Concepto**: Una tabla avanzada que puede agruparse dinamicamente por cobrador, zona, status, dias de atraso, o cualquier columna. Similar a como funcionan las hojas de calculo con agrupacion, pero con acciones integradas y drag-and-drop para reasignar.

**Layout textual**:
```
+-------+-----------------------------------------------------+
| MENU  |  Cuentas de Cobranza                                |
|       |                                                      |
|       |  [Buscar...] [Agrupar por: Cobrador v] [Filtros v]   |
|       |  [Asignar auto] [Solo morosas] [Solo >5 dias]        |
|       |                                                      |
|       |  v EDGAR RAMIREZ (45 cuentas | $38,500 pendiente)    |
|       |  +--------------------------------------------------+|
|       |  | Folio | Cliente  | Atraso | Monto | Status | Acc ||
|       |  |-------|----------|--------|-------|--------|-----||
|       |  | 18501 | Juan P   | 5 dias | $850  | Morosa | [>]||
|       |  | 18502 | Ana G    | 12 dias| $1200 | Vencid | [>]||
|       |  +--------------------------------------------------+|
|       |                                                      |
|       |  v JORGE LOPEZ (38 cuentas | $29,200 pendiente)      |
|       |  +--------------------------------------------------+|
|       |  | 18405 | Maria L  | 8 dias | $1200 | Morosa | [>]||
|       |  +--------------------------------------------------+|
|       |                                                      |
|       |  Drag & drop filas entre grupos para reasignar       |
+-------+-----------------------------------------------------+
```

**Pros**:
- Maxima densidad de informacion en pantalla
- Agrupacion flexible (cambiar con un clic entre cobrador, zona, status)
- Facilita busqueda y filtrado rapido de cuentas especificas
- Familiar para usuarios acostumbrados a Excel
- Soporta acciones en lote (seleccionar multiples y reasignar)

**Contras**:
- Menos visual que kanban para ver la distribucion de carga entre cobradores
- Reasignacion por drag-and-drop es menos intuitiva en tabla que en columnas
- Puede sentirse "fria" sin indicadores visuales de urgencia

---

#### Propuesta 2: Vista de Mapa Primario con Cuentas Geolocalizadas

**Concepto**: El mapa es el elemento principal. Las cuentas se muestran como marcadores en el mapa, coloreados por status/urgencia. Un panel lateral muestra la lista filtrada por lo visible en el mapa. Ideal para planear rutas y ver la distribucion geografica.

**Layout textual**:
```
+-------+-----------------------------------------------------+
| MENU  |  Cuentas de Cobranza               [Lista] [Mapa*]  |
|       |                                                      |
|       |  [Cobrador: EDGAR v] [Status v] [Atraso: >5 dias]    |
|       |                                                      |
|       |  +----------------------------+ +------------------+ |
|       |  |                            | | Cuentas visibles | |
|       |  |    [MAPA INTERACTIVO]      | | (23 en vista)    | |
|       |  |                            | |                  | |
|       |  |  [pin rojo] = >15 dias     | | F:18501 Juan P   | |
|       |  |  [pin narj] = 5-15 dias    | |  $850 | 5 dias   | |
|       |  |  [pin amar] = 1-5 dias     | |  Zona: Centro    | |
|       |  |  [pin verd] = al dia       | |                  | |
|       |  |                            | | F:18502 Ana G    | |
|       |  |  Ruta sugerida: ----->     | |  $1200 | 12 dias | |
|       |  |                            | |  Zona: Zapopan   | |
|       |  |  [Cobrador actual: *]      | |                  | |
|       |  +----------------------------+ | [Generar Ruta]   | |
|       |                                 | [Reasignar sel.] | |
|       |                                 +------------------+ |
+-------+-----------------------------------------------------+
```

**Pros**:
- Excelente para planear rutas de cobranza (se ve donde estan los clientes)
- Visualizacion inmediata de la distribucion geografica de la cartera
- Facilita identificar clusters de cuentas cercanas para asignar a un cobrador
- Integra directamente la funcionalidad de "Rutas de Cobranza" (seccion 10.3)

**Contras**:
- Requiere que la mayoria de clientes tengan direccion geocodificada (PostGIS)
- Menos eficiente para ver datos tabulares detallados (montos, fechas)
- Puede ser lento con miles de marcadores (requiere clustering)
- No todos los usuarios necesitan la vista de mapa (oficina vs campo)

---

#### Propuesta 3: Dashboard de Cobrador Individual con Metricas + Tabla

**Concepto**: Primero se selecciona un cobrador (o se ve un resumen de todos). Se muestra un mini-dashboard con sus metricas personales + tabla de sus cuentas. Enfocado en la gestion individual del rendimiento de cada cobrador.

**Layout textual**:
```
+-------+-----------------------------------------------------+
| MENU  |  Cuentas de Cobranza                                |
|       |                                                      |
|       |  [Cobrador: EDGAR RAMIREZ v]  [Todos los cobradores] |
|       |                                                      |
|       |  +----------+ +----------+ +----------+ +----------+ |
|       |  | Cuentas  | | Cobrado  | | Pendiente| | Eficienc.| |
|       |  |   45     | | $12,300  | | $38,500  | |   68%    | |
|       |  | asignadas| | este mes | | por cobr.| | del mes  | |
|       |  +----------+ +----------+ +----------+ +----------+ |
|       |                                                      |
|       |  +-------------------+ +---------------------------+ |
|       |  | Cobros x Semana   | | Distribucion por status   | |
|       |  | (grafica barras)  | | (grafica dona)            | |
|       |  +-------------------+ +---------------------------+ |
|       |                                                      |
|       |  +--------------------------------------------------+|
|       |  | Folio | Cliente  | Atraso | Monto | Status | Acc ||
|       |  |-------|----------|--------|-------|--------|-----||
|       |  | 18501 | Juan P   | 5 dias | $850  | Morosa | [>]||
|       |  | 18502 | Ana G    | 12 dias| $1200 | Vencid | [>]||
|       |  +--------------------------------------------------+|
|       |  [Reasignar seleccionados] [Asignar auto]            |
+-------+-----------------------------------------------------+
```

**Pros**:
- Enfocado en rendimiento: el gerente ve inmediatamente como va cada cobrador
- Las metricas ayudan a tomar decisiones de reasignacion basadas en datos
- Combina dashboard + tabla en una sola vista
- Facilita la evaluacion de desempeno de cobradores

**Contras**:
- Solo muestra un cobrador a la vez (no se comparan facilmente entre cobradores)
- Requiere cambiar el selector para ver otro cobrador (mas clics)
- Las metricas pueden distraer cuando el objetivo es solo reasignar cuentas
- No muestra la vista geografica (requiere toggle a mapa)

**Endpoints**:
- `GET /api/v1/cards?grouped_by=location&status=active`
- `PUT /api/v1/cards/:id/reassign` -> { new_location }
- `POST /api/v1/cards/auto-assign` (algoritmo de afinidad)
- `GET /api/v1/cards/map` (con coordenadas PostGIS)

### 5.6 Recibos

**Vista actual**: `views/recibos_view.py`

**Que muestra**:
- Titulo "Recibos"
- 2 tabs: "Recibos" y "Asignaciones"
- Tab Recibos: tabla con numero_recibo, folio, cobrador, id_pago, status, fecha_asignacion, fecha_uso, fecha_entrega
- Tab Asignaciones: gestion de asignacion de recibos a cobradores
- Botones: Crear Lote, Asignar a Cobrador, Cancelar Recibo

**Dialogos auxiliares**: CrearLoteDialog (prefijo + rango), AsignarRecibosDialog (seleccionar cobrador).

**Datos del backend**:
- `GET /api/v1/receipts?page=1&per_page=50&status=&cobrador=`
- `POST /api/v1/receipts/batch` (crear lote)
- `POST /api/v1/receipts/assign` (asignar a cobrador)

**Acciones**: Crear lotes de recibos, asignar a cobradores, cancelar recibos (con opcion de revertir pago), buscar recibos.

**Mejoras para web**:
- Dashboard de recibos: total sin asignar, asignados, utilizados, entregados, extraviados
- Alerta de recibos proximos a agotar por cobrador
- Historial de uso de cada recibo (timeline)
- Filtro por cobrador con metricas (cuantos tiene, cuantos uso, cuantos le quedan)
- Vista de "Recibos extraviados" con reporte
- Soporte para recibos electronicos: generacion digital desde la app movil, envio por WhatsApp al cliente, almacenamiento en el sistema con hash de verificacion
- Coexistencia de recibos fisicos y electronicos durante el periodo de transicion
- Indicador de tipo de recibo (fisico/electronico) en la tabla

### 5.7 Cancelaciones

**Vista actual**: `views/cancelaciones_view.py`

**Que muestra**:
- Titulo "Cancelaciones"
- Busqueda
- Filtro por periodo (todas, dia, semana, mes)
- Filtro por codigo de cancelacion
- Tabla: folio, cliente, fecha cancelacion, motivo, codigo (C1-C5), pagos realizados, observaciones
- Acciones: ver detalle, deshacer cancelacion, notificar vendedor/cobrador/cliente
- Paginacion

**Datos del backend**:
- `GET /api/v1/cancellations?page=1&per_page=24&periodo=&codigo=&search=`

**Acciones**: Buscar, filtrar por periodo/codigo, ver detalle, deshacer cancelacion, enviar notificaciones.

**Mejoras para web**:
- Grafica de tendencia de cancelaciones
- Indicador de motivos mas frecuentes (para analisis)
- Boton de cancelar poliza directamente desde esta vista
- Workflow de aprobacion para deshacer cancelaciones
- Colorear por codigo (C5 en naranja, como el sistema actual)

### 5.8 Contado a Cuotas

**Vista actual**: `views/contado_cuotas_view.py`

**Que muestra**:
- Titulo "Contado a Cuotas"
- Busqueda
- Tabla de polizas con forma de pago "Contado 2 Exibiciones" que tienen el segundo pago pendiente/vencido
- Boton para reestructurar pagos (abre dialogo)
- Alerta automatica en la barra principal cuando hay polizas pendientes

**Datos del backend**:
- `GET /api/v1/policies/contado-cuotas-pending`

**Acciones**: Ver polizas candidatas, reestructurar pagos.

**Mejoras para web**:
- Widget de alerta en el dashboard principal
- Notificacion al vendedor responsable
- Preview automatico de restructuracion antes de aplicar

> **CAMBIO DE UBICACION:** Esta vista NO sera independiente. Se integrara dentro del modulo de Pagos
> como una pestana o seccion adicional (ej: Tab "Reestructuraciones" dentro de `/cobranza/pagos`).
> La funcionalidad se mantiene identica pero no justifica una vista separada en el menu.

### 5.9 Promociones

**Vista actual**: `views/promociones_view.py`

**Que muestra**:
- Titulo "Promociones"
- Busqueda, filtro por status (activos/inactivos)
- Tabla: ID, nombre, porcentaje, motivo, status, fecha inicio, fecha fin
- Botones: Agregar, Editar, Activar/Desactivar

**Dialogo**: `views/dialogs/promocion_form_dialog.py` - Formulario con campos basicos.

**Datos del backend**:
- `GET /api/v1/promotions?status=active`
- `POST /api/v1/promotions`
- `PUT /api/v1/promotions/:id`

**Mejoras para web** (CRITICAS -- el sistema actual es MUY limitado):
- Sistema de reglas flexibles: cada promocion tiene multiples beneficios y condiciones
- Tipos de beneficio: descuento %, monto fijo, meses gratis, $0 enganche, upgrade cobertura
- Condiciones: tipo vehiculo, cobertura, forma pago, renovacion, referido, ano vehiculo
- Editor visual de reglas (drag & drop de condiciones y beneficios)
- Preview del impacto: "Si aplicas esta promocion a 50 polizas, el descuento total seria $X"
- Codigo de promocion unico para tracking
- Limite de usos (total y por cliente)
- Programa de referidos integrado
- Dashboard de efectividad de promociones
- Historial de aplicacion (que polizas usaron cada promocion)

### 5.10 Mensajes de Cobranza

**Vista actual**: `views/mensajes_cobranza_view.py`

**Que muestra**:
- Titulo "Mensajes de Cobranza"
- 3 tabs:
  1. **Recordatorios**: Clientes con pagos proximos a vencer (5-3 dias antes). Tabla con folio, cliente, telefono, cobertura, pago, monto, fecha limite, dias restantes, cobrador. Filtros: cobertura, ubicacion. Boton "Enviar a todos" y "Enviar seleccionados".
  2. **Morosos**: Clientes con pagos atrasados/vencidos. Mismos campos + dias de atraso. Filtros: cobertura, ubicacion, status (atrasado/vencido/todos), rango de atraso. Boton envio masivo.
  3. **Historial de Mensajes**: Tabla con folio, tipo mensaje, telefono, fecha envio, exito/error. Filtros: folio, tipo, rango de fechas. Paginacion.

**Datos del backend**:
- `GET /api/v1/messages/reminders`
- `GET /api/v1/messages/delinquent`
- `GET /api/v1/messages/history?page=1&per_page=50`
- `POST /api/v1/messages/send-reminders`
- `POST /api/v1/messages/send-delinquent`

**Acciones**: Cargar candidatos, filtrar, enviar mensajes individuales o masivos, ver historial.

**Mejoras para web**:
- Templates de mensajes editables (sin cambiar codigo)
- Soporte multicanal: WhatsApp + Telegram + SMS + Email
- Programacion de envio (enviar a las 9am del lunes)
- Metricas de entrega: enviados, recibidos, leidos (si WhatsApp Business API lo soporta)
- A/B testing de mensajes
- Opt-out: respetar si el cliente pidio no recibir mas mensajes
- Preview del mensaje antes de enviar
- Cola de envio con progreso (barra de progreso)

### 5.11 Avisos de Visita y Tracking de Rutas

**Vista actual**: `views/avisos_visita_view.py`

**Que muestra**:
- Titulo "Avisos de Visita"
- Busqueda, filtros (pendientes/completados)
- Tabla de avisos de visita programados

**Mejoras para web (AMPLIACION SIGNIFICATIVA)**:

#### Generacion de Avisos con GPS
- Los avisos de visita se generan automaticamente con la ubicacion GPS del cobrador, fecha, hora y minuto que coincida con su ruta programada
- El sistema registra la posicion exacta del cobrador al momento de generar el aviso

#### Tracking en Tiempo Real
- Visualizacion de ruta de cobradores en TIEMPO REAL en el mapa (PostGIS + WebSocket)
- Visualizacion de ruta de ajustadores en TIEMPO REAL (cuando van a un siniestro)
- Marcadores en el mapa que se mueven conforme el cobrador/ajustador avanza
- Panel lateral con lista de cobradores activos y su ultima posicion conocida

#### Rutas Historicas
- Revision de rutas historicas con filtros:
  - Por dia especifico
  - Por semana
  - Por quincena
  - Por mes completo pasado
- Reproduccion de ruta ("replay"): ver el recorrido del cobrador en el mapa como animacion
- Comparacion de ruta planeada vs ruta real recorrida
- Metricas: km recorridos, tiempo en cada parada, eficiencia de ruta

#### Sistema de Ruta Inteligente (App Movil)
- La app movil del cobrador sugiere la ruta optima del dia
- Reordena cuentas por proximidad geografica (nearest neighbor con PostGIS)
- Considera horarios preferidos de los clientes (si se tiene el dato)
- Navegacion punto a punto integrada (abre Waze/Google Maps)

#### Recomendacion Inteligente de Cuentas
- El backend debe recomendar cambio/reasignacion de cuentas basado en:
  - Resultados historicos del cobrador con ese cliente (si nunca logra cobrar, reasignar)
  - Cercania geografica (asignar cuentas cercanas al mismo cobrador)
  - Carga de trabajo actual del cobrador
  - Historial de pago del cliente (clientes que siempre pagan no necesitan cobrador de campo)

> **APLICA SOLO A COBRADORES PUROS.** Este sistema de rutas y tracking NO aplica a vendedores
> ni a ajustadores por default. Los ajustadores tienen su propio tracking cuando van a siniestros.
> Los vendedores no tienen rutas fijas.
>
> Excepcion: los ajustadores que cobran pagos atrasados <5 dias o dinero de contraparte para taller
> usan sus propias rutas de siniestros, no el sistema de rutas de cobranza.

**Layout web**:
```
+-------+-----------------------------------------------------+
| MENU  |  Avisos de Visita y Rutas                            |
|       |                                                      |
|       |  [Tab: Tiempo Real] [Tab: Historico] [Tab: Avisos]   |
|       |                                                      |
|       |  === TAB TIEMPO REAL ===                              |
|       |  +----------------------------+ +------------------+ |
|       |  |                            | | Cobradores (5)   | |
|       |  |    [MAPA EN VIVO]          | |                  | |
|       |  |                            | | EDGAR [en ruta]  | |
|       |  |    * Edgar (moviendose)    | |  Visitas: 3/8    | |
|       |  |    * Jorge (en cliente)    | |  Ultima: 10:32am | |
|       |  |    o Luis  (inactivo)      | |                  | |
|       |  |                            | | JORGE [en client]| |
|       |  +----------------------------+ |  Visitas: 5/12   | |
|       |                                 +------------------+ |
|       |                                                      |
|       |  === TAB HISTORICO ===                                |
|       |  [Cobrador: EDGAR v] [Periodo: Semana v] [Fecha: __] |
|       |  [Mapa con ruta recorrida] [Replay >]                |
|       |  Km: 45.2 | Paradas: 12 | Tiempo: 6h 20min          |
+-------+-----------------------------------------------------+
```

- Integrar con app movil del cobrador
- Status de visita: programada, en camino, completada, no encontrado
- Notificacion push al cobrador

### 5.12 Cobradores

**Vista actual**: `views/cobradores_view.py`

**Que muestra**:
- Titulo "Gestion de Cobradores"
- Busqueda por ID, nombre clave, nombre completo
- Filtro por status (activos/inactivos)
- Tabla: ID, nombre clave, nombre completo, limite recibos, status
- Botones: Agregar, Editar

**Dialogo**: `views/dialogs/cobrador_form_dialog.py`

**Mejoras para web**:
- Agregar campos: telefono, email, zona asignada
- Dashboard por cobrador: tarjetas asignadas, cobros del mes, eficiencia
- Historial de rendimiento (grafica de cobros por mes)
- Configuracion de limite de recibos con sugerencia automatica
- Mapa de zona de cobranza del cobrador

---

## 6. MODULO SINIESTROS

### 6.1 Listado de Siniestros

**Vista actual**: `views/siniestros_view.py` (1668 lineas -- God class)

**Que muestra**:
- Titulo "Siniestros"
- Filtros: busqueda, ajustador (combo), encuestas (combo), periodo (preset + personalizado), rango de fechas
- Tabla: ID, folio, fecha, cliente, vehiculo (marca modelo ano), tipo siniestro, ajustador, status, tiene encuesta
- Colores por status
- Clic derecho: ver detalles, editar, aplicar encuesta de satisfaccion
- Exportar a Excel (con formato especial, encabezados, colores)
- Filtro de badges activos

**Datos del backend**:
- `GET /api/v1/incidents?page=1&per_page=50&ajustador=&periodo=&fecha_desde=&fecha_hasta=&has_survey=`

**Acciones**: Buscar, filtrar, crear siniestro, editar, ver detalles, aplicar encuesta, exportar Excel.

**Mejoras para web**:
- Separar logica de negocio de la vista (actualmente mezcla SQL + UI + reportes)
- Mapa de ubicacion de siniestros (PostGIS)
- Dashboard de siniestros: por tipo, por zona, por ajustador, tendencia mensual
- Workflow visual: nuevo -> asignado -> en proceso -> resuelto -> cerrado
- Carga de fotos del siniestro desde app movil
- Documentos adjuntos (acta, peritaje, dictamen)
- Timeline de eventos del siniestro
- Notificaciones en tiempo real cuando se asigna un siniestro

**Layout web**:
```
+-------+---------------------------------------------+
| MENU  |  Siniestros                   [+ Nuevo]      |
|       |                                              |
|       |  [Buscar...] [Ajustador v] [Periodo v]       |
|       |  [Desde: __] [Hasta: __] [Encuestas v]       |
|       |  [Exportar Excel]                            |
|       |                                              |
|       |  +------------------------------------------+|
|       |  | ID | Folio | Fecha | Cliente | Tipo | ...||
|       |  +------------------------------------------+|
|       |                                              |
|       |  [< 1 2 3 ... >]                             |
+-------+---------------------------------------------+
```

### 6.2 Formulario de Siniestro (Crear/Editar)

**Dialogo actual**: `views/dialogs/siniestros/incident_dialog.py` + `incident_ui.py` + `incident_data.py`

**Que muestra**: Formulario con: folio de poliza (busqueda), datos del cliente (auto-cargados), datos del vehiculo, datos del siniestro (tipo, fecha, hora, descripcion, ubicacion/municipio), ajustador asignado, observaciones, status.

**Se registra como "dialogo critico"** para evitar cierre de sesion.

**Acciones**: Buscar poliza, seleccionar ajustador, guardar, notificar grupo Telegram de siniestros.

**Mejoras para web**:
- Formulario en pagina completa (no modal)
- Autocompletar folio con preview de poliza/cliente
- Seleccion de ubicacion en mapa
- Carga de fotos directa (drag & drop)
- Asignacion automatica de ajustador segun turno actual
- Validacion de elegibilidad de servicio en tiempo real

### 6.3 Detalle de Siniestro

**Dialogo actual**: `views/dialogs/siniestros/incident_details.py`

**Que muestra**:
- Datos del siniestro en tabs
- Tab: Datos generales (tipo, fecha, descripcion, ajustador, status)
- Tab: Pases de taller (workshop passes)
- Tab: Pases medicos (medical passes)
- Encuesta de satisfaccion
- Historial de cambios

**Mejoras para web**: Pagina completa con URL `/siniestros/:id`, tabs + timeline + fotos.

### 6.4 Pases de Taller y Medicos

**Dialogos**: `workshop_pass_dialog.py`, `medical_pass_dialog.py`

**Que muestran**: Formularios para registrar pases de taller (enviar vehiculo a reparacion) y pases medicos (atencion a lesionados).

**En web**: Modales dentro del detalle del siniestro.

### 6.5 Encuesta de Satisfaccion de Siniestro

**Dialogo**: `incident_satisfaction_survey_dialog.py`

**Que muestra**: Formulario de encuesta con preguntas de satisfaccion sobre el servicio del ajustador.

**En web**: Modal o seccion desplegable en detalle del siniestro.

---

## 7. MODULO GRUAS

### 7.1 Listado de Servicios de Grua

**Vista actual**: `views/gruas_view.py` (1098 lineas)

**Que muestra**:
- Titulo "Servicios de Grua"
- Filtros: busqueda, proveedor (combo), encuestas, periodo (preset + personalizado), rango de fechas
- Tabla: ID, folio, fecha, hora, cliente, vehiculo, origen (municipio), destino, proveedor, costo, status, tiene encuesta
- Clic derecho: ver detalles, editar, encuesta de satisfaccion
- Exportar a Excel
- Filtro de badges

**Datos del backend**:
- `GET /api/v1/tow-services?page=1&per_page=50&proveedor=&periodo=&fecha_desde=&fecha_hasta=`

**Acciones**: Buscar, filtrar, crear servicio de grua, ver detalles, editar, aplicar encuesta, exportar.

**Mejoras para web**:
- Mapa con origen y destino de cada servicio (PostGIS)
- Dashboard: total servicios del mes, costo promedio, proveedor mas usado
- Verificacion automatica de servicios disponibles por poliza
- Lista de proveedores cercanos al siniestro (ordenados por distancia)
- Tracking en tiempo real de la grua (GPS del proveedor)
- Boton "Solicitar Grua" con flujo completo de validacion de elegibilidad

### 7.2 Formulario de Servicio de Grua

**Dialogo actual**: `views/dialogs/gruas/tow_service_dialog.py` + multiples archivos auxiliares

**Subcomponentes**:
- `tow_service_ui.py`: Layout del formulario
- `tow_service_data.py`: Carga de datos (proveedores, municipios)
- `tow_service_edit.py`: Edicion de servicio existente
- `tow_service_validators.py`: Validaciones
- `tow_service_providers.py`: Gestion de proveedores en el formulario
- `tow_service_notifications.py`: Notificaciones Telegram
- `tow_service_database.py`: Operaciones de BD
- `quote_providers_dialog.py`: Cotizacion de proveedores
- `tow_service_details.py`: Vista de detalles

**Se registra como "dialogo critico"**.

**Que muestra**: Folio (busqueda), datos del cliente y poliza (auto-cargados), validacion de elegibilidad, seleccion de proveedor, municipio origen/destino, costo, observaciones.

**Mejoras para web**:
- Wizard: Paso 1: Buscar poliza -> Paso 2: Validar elegibilidad -> Paso 3: Seleccionar proveedor mas cercano (mapa) -> Paso 4: Confirmar
- Mapa interactivo para seleccionar origen y destino
- Lista de proveedores cercanos ordenados por distancia (PostGIS)
- Calculo automatico de costo estimado por distancia

### 7.3 Encuesta de Satisfaccion de Grua

**Dialogo**: `views/dialogs/gruas/tow_satisfaction_survey_dialog.py`

**Que muestra**: Formulario de encuesta sobre calidad del servicio de grua.

---

## 8. MODULO ENDOSOS

### 8.1 Listado de Endosos

**Vista actual**: `views/endosos_view.py`

**Que muestra**:
- Titulo "Endosos"
- Filtros: tipo (cambio de placas, cambio de vehiculo, cambio de cobertura, cambio de contratante, cesion de derechos), estado, busqueda
- Tabla: ID, folio, tipo, fecha, datos anteriores, datos nuevos, status, creado por
- Paginacion (24 items)
- Doble clic: ver detalle del endoso

**Datos del backend**:
- `GET /api/v1/endorsements?page=1&per_page=24&tipo=&estado=&search=`

**Acciones**: Buscar, filtrar por tipo/estado, crear nuevo endoso, ver detalle.

**Subcomponentes de endoso** (widgets dentro de poliza_form):
- `endoso_widget.py`: Formulario principal de endoso
- `endoso_edit_widget.py`: Edicion de endoso existente
- `endoso_details_widget.py`: Vista de detalle
- Formularios por tipo:
  - `plate_change_form.py`: Cambio de placas (placas anteriores -> nuevas)
  - `vehicle_change_form.py`: Cambio de vehiculo (vehiculo anterior -> nuevo)
  - `contractor_change_form.py`: Cambio de contratante
  - `rights_transfer_form.py`: Cesion de derechos

**Mejoras para web**:
- Formulario dinamico que cambia segun el tipo de endoso
- Previsializacion de cambios (antes vs despues)
- Calculo automatico del costo del cambio de cobertura (para endosos de cambio de cobertura, calcular diferencia de prima y mostrar el monto al usuario antes de confirmar)
- Workflow de aprobacion para endosos que afecten cobertura
- Historial de endosos por poliza (timeline)
- Generacion automatica de documento de endoso (PDF)
- Opcion de enviar detalles del cambio por mensaje (WhatsApp) al cliente, al vendedor, o a ambos

---

## 9. MODULO ADMINISTRACION

### 9.1 Vendedores

**Vista actual**: `views/vendedores_view.py`

**Que muestra**:
- Titulo "Vendedores"
- Busqueda, filtro por status (activos/inactivos/todos)
- Tabla: ID, nombre completo, clase, meta, Telegram ID, status
- Botones: Agregar, Editar, Activar/Desactivar

**Dialogo**: `views/dialogs/vendedor_form_dialog.py`

**Mejoras para web**:
- Dashboard por vendedor: polizas vendidas, meta vs actual, comisiones
- Grafica de rendimiento mensual
- Ranking de vendedores
- Configuracion de metas mensuales
- Historial de comisiones

**Endpoints**:
- `GET /api/v1/sellers?status=active`
- `POST /api/v1/sellers`
- `PUT /api/v1/sellers/:id`
- `GET /api/v1/sellers/:id/performance`

### 9.2 Coberturas

**Vista actual**: `views/coverages_view.py`

**Que muestra**:
- Titulo "Coberturas"
- Busqueda, filtro por tipo de vehiculo, filtro por estado
- Tabla: ID, tipo vehiculo, clave vehicular, nombre cobertura, tipo servicio, cilindraje, precio credito, enganche, precio contado, gruas disponibles, activa
- Botones: Agregar, Editar, Activar/Desactivar

**Dialogo**: `views/dialogs/coverage_form_dialog.py`

**Mejoras para web**:
- Vista de comparacion de coberturas (tabla comparativa)
- Historial de cambios de precios
- Carga masiva de precios desde Excel
- Preview del impacto de un cambio de precio ("Afectaria a X polizas activas")

### 9.3 Ajustadores

**Vista actual**: `views/adjusters_view.py`

**Que muestra**:
- Titulo "Ajustadores"
- Busqueda, filtro por status
- Tabla: ID, nombre, patron de clave (M01, M02...), telefono, status
- Botones: Agregar, Editar

**Dialogo**: `views/dialogs/adjuster_form_dialog.py`

**Mejoras para web**:
- Dashboard por ajustador: siniestros atendidos, encuestas de satisfaccion, tiempo promedio de respuesta
- Mapa de cobertura de zona del ajustador
- Disponibilidad en tiempo real (conectado con app movil)

### 9.4 Guardias de Ajustadores

**Vista actual**: `views/adjuster_shifts_view.py`

**Que muestra**:
- Titulo con navegacion mes anterior/siguiente
- Calendario mensual en formato tabla: filas = ajustadores, columnas = dias del mes
- Cada celda tiene un combo con opciones: 1 (primera guardia), 2 (segunda), 3 (tercera), D (descanso)
- Colores: verde=1ra guardia, amarillo=2da, naranja=3ra, gris=descanso
- Boton de generar guardias automaticamente

**Datos del backend**:
- `GET /api/v1/shifts?month=2&year=2026`
- `PUT /api/v1/shifts`

**Acciones**: Navegar entre meses, asignar turnos manualmente, generar turnos automaticamente, guardar cambios.

**Mejoras para web**:
- Vista de calendario tipo Google Calendar
- Drag & drop para asignar turnos
- Notificacion automatica de turno al ajustador (09:00 diariamente, ya existe)
- Reglas configurables de rotacion
- Vista semanal ademas de mensual
- Indicador de horas trabajadas por ajustador

### 9.5 Renovaciones

**Vista actual**: `views/renovaciones_view.py`

**Que muestra**:
- Titulo "Renovaciones"
- Filtros: rango de fechas, filtro de cobertura, filtro de status
- Tabla: folio, folio contrato, cliente, cobertura, vigencia, fin vigencia, dias restantes, vendedor, status poliza, elegible AMPLIA SELECT, tiene endosos, tiene siniestros, tiene servicios grua, codigo cancelacion (C5 en naranja)
- Boton de exportar a Excel (4 hojas: renovaciones, endosos, gruas, siniestros)
- Boton de refrescar

**Datos del backend**:
- `GET /api/v1/renewals?fecha_desde=&fecha_hasta=&cobertura=&status=`
- `GET /api/v1/renewals/export`

**Acciones**: Filtrar, ver polizas proximas a vencer, exportar reporte, identificar elegibilidad AMPLIA SELECT.

**Mejoras para web**:
- Dashboard de renovaciones: total proximas a vencer, renovadas vs perdidas, tasa de renovacion
- Funnel: proximas a vencer -> contactadas -> cotizadas -> renovadas
- Asignacion automatica a vendedores para seguimiento
- Envio masivo de recordatorios de renovacion al cliente
- Indicador de "riesgo de perdida" basado en historial de pago
- Boton "Renovar" directo que abre el formulario pre-llenado

> **NOTA:** Se discutira a detalle mas adelante. Las renovaciones son un flujo complejo que involucra
> vendedores, cotizaciones, y seguimiento. Los detalles de este modulo se definiran cuando se inicie
> su desarrollo.

### 9.6 Proveedores de Gruas

**Vista actual**: `views/tow_providers_view.py`

**Que muestra**:
- Titulo "Proveedores de Gruas"
- Busqueda, filtro por status
- Tabla: ID, nombre, telefono, direccion, zona de cobertura, status
- Botones: Agregar, Editar, Activar/Desactivar

**Dialogo**: `views/dialogs/tow_provider_form_dialog.py`

**Mejoras para web**:
- Mapa de zona de cobertura de cada proveedor (PostGIS)
- Ranking de proveedores por calidad de servicio (encuestas)
- Historial de servicios por proveedor
- Tarifario configurable por distancia/zona

### 9.7 Administracion de Usuarios

**Vista actual**: `views/admin_usuarios_view.py`

**Que muestra**:
- Titulo "Administracion de Usuarios"
- Tabla: ID, username, nombre, departamento, rol, status
- Botones: Nuevo Usuario, Editar, Eliminar
- Formulario con: username, contrasena, nombre, departamento (combo), rol (combo), permisos (checkboxes)

**Datos del backend**:
- `GET /api/v1/users`
- `POST /api/v1/users`
- `PUT /api/v1/users/:id`

**Mejoras para web**:
- Gestion de roles con matriz de permisos visual
- Auditoria: log de acciones por usuario
- Sesiones activas (ver quien esta conectado)
- Politicas de contrasena configurables
- Invitacion por email para nuevos usuarios
- Foto de perfil

> **UNIFICACION DE EMPLEADOS:** Vendedores, cobradores y ajustadores deben unificarse en una sola
> tabla de EMPLEADOS. Un empleado puede tener multiples roles y pertenecer a multiples departamentos.
> Las tablas separadas de `seller`, `collector`, `adjuster` se reemplazan por una tabla `employee`
> con relacion muchos-a-muchos a `role`.
>
> **Referencia:** La rama `feature/vacaciones-whatsapp-cobradores` tiene un prototipo de esta estructura
> unificada. Se tomara la idea de esa rama pero mejorada e integrada con el nuevo sistema de roles RBAC.
>
> **Ejemplo:** Un registro de empleado "Juan Perez" puede tener:
> - Roles: [vendedor, cobrador]
> - Departamentos: [ventas, cobranza]
> - Permisos efectivos: union de permisos de vendedor + cobrador

---

## 10. VISTAS NUEVAS PROPUESTAS

Estas pantallas NO existen en el sistema actual y deben disenarse desde cero.

### 10.1 Panel de Autorizacion de Polizas

**Proposito**: Los vendedores suben polizas desde la app movil. La oficina las revisa aqui.

**Que muestra**:
- Lista de polizas pendientes de autorizacion
- Para cada poliza: datos del vehiculo, datos del cliente, cobertura, fotos del contrato
- Status: pendiente, en revision, aprobada, rechazada (con correcciones)
- Filtros: por vendedor, por fecha, por status

**Acciones**:
- Revisar poliza
- Aprobar (con o sin observaciones)
- Rechazar con motivo y correcciones necesarias
- Re-enviar al vendedor para correccion

**Layout web**:
```
+-------+---------------------------------------------+
| MENU  |  Autorizacion de Polizas     [3 pendientes]  |
|       |                                              |
|       |  [Vendedor v] [Status v] [Fecha v]           |
|       |                                              |
|       |  +------------------+  +-------------------+ |
|       |  | Lista pendientes |  | Detalle seleccion | |
|       |  |                  |  |                   | |
|       |  | V01 - 14/02      |  | Folio: 18510     | |
|       |  | AMPLIA - AUTO    |  | Cliente: Juan P  | |
|       |  | Juan Perez    -->|  | Vehiculo: ...    | |
|       |  |                  |  | [Foto contrato]  | |
|       |  | V02 - 14/02      |  |                   | |
|       |  | PLATINO - PICKUP |  | [APROBAR] [RECH.] | |
|       |  | Maria Lopez      |  | Observaciones:    | |
|       |  |                  |  | [_______________] | |
|       |  +------------------+  +-------------------+ |
+-------+---------------------------------------------+
```

**Endpoints**:
- `GET /api/v1/policy-approvals?status=pending&vendedor_id=`
- `POST /api/v1/policy-approvals/:id/approve`
- `POST /api/v1/policy-approvals/:id/reject`
- `POST /api/v1/policy-approvals/:id/request-correction`

### 10.2 Panel de Autorizacion de Pagos

> **UNIFICADO con seccion 5.3 (Pagos Temporales / Pendientes de Autorizacion).**
> Esta vista NO es separada. Los "pagos temporales", la "revision de pagos" y el "panel de autorizacion
> de pagos" son el MISMO concepto: pagos que necesitan revision antes de aplicarse.
>
> Toda la funcionalidad se consolida en una sola pantalla en `/cobranza/autorizaciones` (seccion 5.3).
> La seccion 5.4 (Revision de Pagos) tambien se unifica aqui.
>
> Ver seccion 5.3 para el diseno completo de esta pantalla unificada.

**Funcionalidad consolidada** (todo en una sola vista con pestanas/filtros):
- Lista de pagos pendientes de autorizacion (propuestas de cobradores desde la app)
- Comparacion con pago original (monto esperado vs registrado)
- Ubicacion GPS donde se registro el pago
- Foto del recibo/baucher subida desde app movil
- Flujo: pendiente -> en revision -> aprobado (se aplica al pago original) / rechazado (con motivo)
- Indicador de montos altos (>$5000 requiere gerente)
- Revision de pago: verificar recibo, sincronizar, notificar WhatsApp
- Historial de aprobaciones/rechazos con auditoria

**Endpoints** (mismos que seccion 5.3):
- `GET /api/v1/authorization/payments?status=pending`
- `POST /api/v1/authorization/payments/:id/approve`
- `POST /api/v1/authorization/payments/:id/reject`
- `POST /api/v1/authorization/payments/:id/apply` (aplicar al pago original tras revision)
- `POST /api/v1/authorization/payments/:id/escalate`
- `GET /api/v1/authorization/payments/:id/history`

### 10.3 Vista de Rutas de Cobranza

**Proposito**: Mapa con clientes morosos para planear rutas optimas de cobranza.

**Que muestra**:
- Mapa interactivo (Leaflet/Mapbox con datos de PostGIS)
- Marcadores por cliente moroso con color segun dias de atraso
- Informacion en popup: folio, cliente, monto, dias atraso, telefono
- Panel lateral con lista de clientes en la zona visible
- Filtros: cobrador, zona, rango de atraso, monto minimo
- Ruta optimizada sugerida (linea en mapa)
- Ubicacion actual del cobrador (si tiene app movil activa)

**Acciones**:
- Filtrar clientes morosos por zona
- Generar ruta optimizada (PostGIS nearest neighbor)
- Asignar ruta a cobrador
- Enviar ruta a app movil del cobrador
- Ver historico de visitas en cada punto

**Layout web**:
```
+-------+---------------------------------------------+
| MENU  |  Rutas de Cobranza                           |
|       |                                              |
|       |  [Cobrador v] [Zona v] [Atraso: >5 dias]     |
|       |                                              |
|       |  +---------------------+ +------------------+|
|       |  |                     | | Clientes (12)    ||
|       |  |   [MAPA INTERACTIVO]| | F:18501 Juan P   ||
|       |  |   con marcadores    | |   $850 - 12 dias ||
|       |  |   y ruta optima     | | F:18405 Maria L  ||
|       |  |                     | |   $1200 - 8 dias ||
|       |  |   [pin] [pin]       | | ...              ||
|       |  |    \   /            | |                  ||
|       |  |     ---             | | [Generar Ruta]   ||
|       |  |                     | | [Enviar a app]   ||
|       |  +---------------------+ +------------------+|
+-------+---------------------------------------------+
```

**Endpoints**:
- `GET /api/v1/collections/map?cobrador_id=&min_days=5&bbox=lat1,lng1,lat2,lng2`
- `POST /api/v1/collections/route/optimize` -> { points: [...], optimized_order: [...] }
- `POST /api/v1/collections/route/assign` -> { cobrador_id, route_points: [...] }

### 10.4 Gestion de Promociones (Avanzada)

**Proposito**: Crear, editar y gestionar promociones con reglas flexibles. Reemplaza la vista actual limitada.

**Que muestra**:
- Dashboard de promociones: activas, expiradas, por vencer, usos totales
- Lista de promociones con: codigo, nombre, tipo(s) de beneficio, vigencia, usos/limite, status
- Formulario de creacion con constructor de reglas
- Seccion de beneficios: agregar multiples (descuento %, meses gratis, $0 enganche, etc.)
- Seccion de condiciones: agregar multiples (tipo vehiculo, cobertura, renovacion, etc.)
- Preview del impacto
- Historial de aplicacion

**Layout web**:
```
+-------+---------------------------------------------+
| MENU  |  Promociones                  [+ Nueva]      |
|       |                                              |
|       |  +--------+ +--------+ +--------+ +--------+|
|       |  |Activas | |Expirad | |Usos hoy| |Descuent||
|       |  |   5    | |   12   | |   23   | | $45K   ||
|       |  +--------+ +--------+ +--------+ +--------+|
|       |                                              |
|       |  +------------------------------------------+|
|       |  | Codigo  | Nombre    | Beneficio | Usos   ||
|       |  |---------|-----------|-----------|--------||
|       |  | MAYO26  | Prom. May | -15%      | 23/100 ||
|       |  | REF100  | Referidos | -10% ambos| 8/inf  ||
|       |  | 0ENGANC | Sin Engan | $0 engch  | 5/50   ||
|       |  +------------------------------------------+|
+-------+---------------------------------------------+
```

### 10.5 Centro de Notificaciones

**Proposito**: Historial unificado de todas las comunicaciones enviadas.

**Que muestra**:
- Tabs por canal: WhatsApp | Telegram | SMS | Email | Todos
- Tabla: fecha, destinatario, tipo (pago, moroso, recordatorio, cancelacion, renovacion), canal, status (enviado/fallido/leido), mensaje
- Filtros: folio, tipo mensaje, canal, rango de fechas, status
- Paginacion
- Metricas: total enviados, tasa de entrega, fallos
- Templates de mensajes editables

**Acciones**:
- Buscar mensajes por folio/destinatario
- Reenviar mensaje fallido
- Ver detalle del mensaje
- Editar templates
- Configurar reglas de envio automatico

**Endpoints**:
- `GET /api/v1/notifications/history?channel=&type=&folio=&page=1`
- `GET /api/v1/notifications/stats`
- `GET /api/v1/notifications/templates`
- `PUT /api/v1/notifications/templates/:id`
- `POST /api/v1/notifications/:id/resend`

### 10.6 Reportes Avanzados

**Proposito**: Centro de reportes con generacion configurable.

**Que muestra**:
- Reportes predefinidos: polizas, pagos, cobranza, siniestros, gruas, renovaciones, comisiones
- Filtros por fecha, vendedor, cobrador, cobertura, status
- Preview del reporte en pantalla
- Exportar a Excel, PDF, CSV
- Reportes programados (envio automatico por email)
- Graficas configurables

**Reportes clave**:
- Reporte diario de cobranza (ya existe como Excel en pagos temporales)
- Reporte de renovaciones con 4 hojas (ya existe)
- Reporte de comisiones por vendedor
- Reporte de siniestros por periodo
- Reporte de morosos con antiguedad de deuda
- KPIs mensuales del negocio

---

## 11. APPS MOVILES

### 11.1 App Cobrador

**Plataforma**: React Native (iOS + Android)

**Pantallas**:

1. **Login**: Credenciales del sistema, biometria opcional (huella/face)

2. **Home / Dashboard**:
   - Tarjetas asignadas hoy
   - Cobros realizados hoy (monto total)
   - Ruta del dia (si fue asignada)
   - Notificaciones pendientes

3. **Mis Tarjetas** (lista):
   - Lista de folios asignados
   - Filtros: morosos, pendientes, todos
   - Ordenar: por urgencia, por distancia, por monto
   - Color por status

4. **Detalle de Tarjeta**:
   - Datos del cliente (nombre, telefono, direccion)
   - Datos de la poliza (folio, cobertura, vigencia)
   - Pagos pendientes con montos y fechas
   - Boton "Llamar cliente"
   - Boton "Navegar" (abre Google Maps/Waze)
   - Boton "Registrar cobro"

5. **Registrar Cobro**:
   - Seleccionar pago a cobrar
   - Ingresar monto cobrado
   - Seleccionar metodo de pago
   - Ingresar numero de recibo (con scanner de codigo de barras)
   - Tomar foto del recibo/baucher
   - GPS automatico de ubicacion
   - Confirmar y enviar (queda como "pendiente de autorizacion")

6. **Mis Cobros del Dia**:
   - Lista de cobros registrados hoy
   - Status: pendiente, aprobado, rechazado
   - Monto total del dia

7. **Dinero Pendiente por Entregar**:
   - Resumen de todo el dinero cobrado que aun no se ha entregado a la empresa
   - Desglose por dia de cobro, metodo de pago, y cliente
   - Monto total acumulado pendiente de entregar
   - Notificacion de alerta automatica cuando el monto acumulado llega a un umbral configurado
     (ej: al acumular $5,000 sin depositar -> notificacion push "Tienes $5,000 pendientes de entregar. Deposita lo antes posible.")
   - Historial de entregas/depositos realizados

8. **Ruta del Dia**:
   - Mapa con puntos de visita
   - Navegacion punto a punto
   - Marcar visita como "realizada" o "cliente no encontrado"

9. **Notificaciones Push**:
   - Cobro aprobado/rechazado
   - Nueva tarjeta asignada
   - Ruta del dia asignada
   - Aviso de visita programado
   - Alerta de dinero acumulado pendiente de entregar (al superar umbral configurado)

**Funcionalidad adicional**:
- Opcion de imprimir recibo desde la app usando impresora portatil Bluetooth (para clientes que soliciten recibo fisico)
- Generacion de recibo electronico enviable por WhatsApp al cliente

**Endpoints que consume**:
- `GET /api/v1/collections/my-cards`
- `GET /api/v1/cards/:id/payments`
- `POST /api/v1/authorization/payments`
- `GET /api/v1/authorization/payments/mine`
- `GET /api/v1/collections/route/mine`
- `POST /api/v1/receipts/verify`
- `POST /api/v1/files/upload` (foto recibo)
- `GET /api/v1/collections/my-pending-money` (dinero pendiente por entregar)
- `POST /api/v1/collections/my-deposits` (registrar entrega/deposito)
- `POST /api/v1/receipts/print` (generar recibo para impresion portatil)
- `POST /api/v1/receipts/send-digital` (enviar recibo electronico por WhatsApp)

### 11.2 App Vendedor

**Plataforma**: React Native (iOS + Android)

**Pantallas**:

1. **Login**: Credenciales del sistema

2. **Home / Dashboard**:
   - Polizas vendidas este mes vs meta
   - Barra de progreso de meta
   - Renovaciones pendientes
   - Comisiones del mes

3. **Mis Polizas** (lista):
   - Polizas creadas por mi
   - Filtros: activas, pendientes, expiradas
   - Busqueda por folio/cliente
   - Indicador visible de si el cliente ya realizo el primer pago (necesario para cobrar comision)
   - Icono/badge: "Primer pago: Pagado" / "Primer pago: Pendiente"

4. **Nueva Poliza** (wizard):
   - Paso 1: Buscar/crear cliente
   - Paso 2: Datos del vehiculo (con opcion de scanner VIN)
   - Paso 3: Seleccionar cobertura y forma de pago
   - Paso 4: Tomar foto del contrato firmado
   - Paso 5: Confirmar y enviar (queda pendiente de autorizacion)

5. **Cotizaciones**:
   - Crear nueva cotizacion
   - Ver mis cotizaciones
   - Compartir cotizacion por WhatsApp al cliente

6. **Renovaciones Pendientes**:
   - Lista de polizas proximas a vencer de mis clientes
   - Boton "Contactar cliente"
   - Boton "Iniciar renovacion"

7. **Mis Comisiones**:
   - Desglose de comisiones por poliza
   - Total del mes
   - Historial de meses anteriores

8. **Notificaciones Push**:
   - Poliza aprobada/rechazada
   - Cancelacion de poliza propia
   - Renovacion proxima a vencer
   - Meta alcanzada

**Endpoints que consume**:
- `GET /api/v1/policies/mine`
- `POST /api/v1/policy-proposals` (poliza pendiente de autorizacion)
- `GET /api/v1/renewals/mine`
- `GET /api/v1/sellers/me/commissions`
- `GET /api/v1/quotes/mine`
- `POST /api/v1/quotes`

### 11.3 App Ajustador

**Plataforma**: React Native (iOS + Android)

**Pantallas**:

1. **Login**: Credenciales del sistema

2. **Home / Dashboard**:
   - Turno actual (guardia 1, 2, 3 o descanso)
   - Siniestros asignados pendientes
   - Proximo turno

3. **Mi Turno**:
   - Calendario semanal con mis turnos
   - Indicador de "en guardia" / "disponible" / "en descanso"

4. **Siniestros Asignados**:
   - Lista de siniestros que me asignaron
   - Status: nuevo, en camino, en sitio, resuelto
   - Filtro por status

5. **Detalle de Siniestro**:
   - Datos del cliente y poliza
   - Datos del vehiculo
   - Ubicacion del siniestro (mapa)
   - Boton "En camino" (actualiza status y comparte GPS)
   - Boton "Llegue al sitio"
   - Formulario de reporte:
     - Descripcion del dano
     - Tomar fotos (multiples)
     - Croquis del accidente (dibujo simple)
     - Datos de terceros involucrados
     - Firma del asegurado (captura de firma)
   - Boton "Solicitar grua" (si aplica)
   - Boton "Marcar como resuelto"

6. **Mis Reportes**:
   - Historial de siniestros atendidos
   - Encuestas de satisfaccion recibidas

7. **Notificaciones Push**:
   - Nuevo siniestro asignado
   - Turno proximo a iniciar
   - Encuesta de satisfaccion completada

> **FUNCIONALIDADES FUTURAS (se detallara cuando estemos por comenzar con la app):**
> - Generar pase de taller directamente desde la app (con datos del vehiculo, taller, y presupuesto)
> - Captura de danos de vehiculos con fotos anotadas (marcar zonas danadas sobre diagrama del vehiculo)
> - Generar pases medicos desde la app
> - Croquis del accidente usando Maps (dibujo sobre mapa real, no solo boceto)
> - Guia paso a paso de procedimientos (checklist interactivo para cada tipo de siniestro)
> - Mensajes de voz tipo walkie-talkie entre ajustadores y oficina (comunicacion rapida sin llamada telefonica)
>
> Estas funcionalidades se disenaraN y documentaraN en detalle cuando el desarrollo de la app
> de ajustadores este proximo a comenzar.

**Endpoints que consume**:
- `GET /api/v1/incidents/assigned-to-me`
- `PUT /api/v1/incidents/:id/status` (en camino, en sitio, resuelto)
- `POST /api/v1/incidents/:id/photos`
- `POST /api/v1/incidents/:id/report`
- `GET /api/v1/shifts/mine`
- `POST /api/v1/tow-services` (solicitar grua desde campo)

---

## 12. NAVEGACION GLOBAL Y LAYOUT

### 12.1 Estructura del Sistema Actual (Desktop)

El sistema actual tiene una ventana principal (`main_window.py`) con:
- **Menu lateral izquierdo** con 7 botones principales:
  1. Dashboard
  2. Gruas
  3. Siniestros
  4. Clientes
  5. Polizas
  6. Administracion (submenu desplegable con 7 items)
  7. Cobranza (submenu desplegable con 12 items)
- **Stack de contenido** central que cambia segun el boton presionado (25 vistas)
- **Header** con logo, info de usuario, menu de perfil (cambiar contrasena, cerrar sesion)
- Control de acceso por roles/departamentos (menu items visibles segun permisos)

### 12.2 Propuesta de Navegacion Web

**Sidebar colapsable** con iconos y texto:

```
+------------------+
| [LOGO PROTEGRT]  |
|------------------|
| Dashboard        |
| Clientes         |
| Polizas          |
| Cobranza  >      |
|   Dashboard      |
|   Pagos          |
|   Autorizaciones |
|   Cuentas        |
|   Recibos        |
|   Cancelaciones  |
|   Mensajes       |
|   Promociones    |
|   Rutas y Visitas|
| Siniestros >     |
|   Listado        |
|   Dashboard      |
| Gruas            |
| Endosos          |
| Renovaciones     |
| RRHH  >          |
|   Mi Panel       |
|   Vacaciones     |
|   Permisos       |
|   Horarios       |
| Admin  >         |
|   Empleados      |
|   Coberturas     |
|   Guardias       |
|   Proveedores    |
|   Usuarios       |
| Reportes         |
| Notificaciones   |
|------------------|
| [Perfil usuario] |
| [Cerrar sesion]  |
+------------------+
```

> **CAMBIOS EN EL MENU:**
> - **Siniestros** ahora es una seccion con submenu (listado + dashboard de siniestros)
> - **RRHH** es un nuevo departamento: cada empleado accede a su panel personal (vacaciones, permisos sin goce, horario, quejas/sugerencias)
> - **Empleados** reemplaza a "Vendedores", "Ajustadores" (como items separados). Un empleado puede
>   tener multiples roles. Las metricas especificas de vendedores/cobradores/ajustadores se mueven
>   a los dashboards de cada departamento.
>
> **A DISCUTIR:** Posiblemente unificar vendedores/cobradores/ajustadores completamente en "Empleados"
> y que las vistas especificas (ranking de vendedores, eficiencia de cobradores, etc.) sean
> dashboards dentro de cada departamento en lugar de secciones de admin.

### 12.3 Principios de Diseno Web

1. **Responsivo**: Funcional en desktop (1920x1080) y tablet (1024x768). No necesita ser mobile-first (las apps moviles son separadas).

2. **Tema**: Colores institucionales de Protegrt. Modo claro por default, modo oscuro opcional.

3. **Tablas**: Todas las tablas deben tener:
   - Ordenamiento por columna (click en header)
   - Filtros por columna
   - Columnas configurables (mostrar/ocultar)
   - Exportar a Excel/CSV/PDF (excepto tabla de clientes por politica de seguridad)
   - Paginacion con selector de items por pagina (10/25/50/100)
   - Busqueda global en header

4. **Formularios**:
   - Validacion en tiempo real (sin esperar submit)
   - Campos obligatorios marcados con asterisco
   - Mensajes de error inline (debajo del campo)
   - Auto-guardado en borradores (para formularios largos como polizas)
   - Confirmacion antes de descartar cambios no guardados

5. **Notificaciones en tiempo real** (WebSocket):
   - Badge con contador en items del menu
   - Toast notifications para eventos criticos
   - Panel de notificaciones desplegable
   - Sonido configurable para alertas urgentes

6. **Accesibilidad**:
   - Atajos de teclado para acciones frecuentes
   - Contraste adecuado para legibilidad
   - Navegacion completa por teclado

### 12.4 Tecnologias de Frontend Sugeridas

- **Framework**: Next.js 14+ (App Router)
- **UI Library**: shadcn/ui (sobre Radix UI + Tailwind CSS)
- **Tablas**: TanStack Table (ex React Table)
- **Graficas**: Recharts o Chart.js
- **Mapas**: Leaflet con react-leaflet + PostGIS tiles
- **Estado**: Zustand o React Query (TanStack Query) para cache de servidor
- **Formularios**: React Hook Form + Zod
- **Drag & Drop**: dnd-kit (para kanban de tarjetas)
- **Notificaciones**: WebSocket con Socket.io o Server-Sent Events
- **Internacionalizacion**: next-intl (espanol por default)

---

## APENDICE A: MAPEO DE VISTAS ACTUALES A PANTALLAS WEB

| Vista Desktop (PyQt5) | Ruta Web Propuesta | Cambios principales |
|----------------------|-------------------|-------------------|
| `login_view.py` | `/login` | Agregar forgot password, 2FA. ELIMINADO: acceso anonimo, recordar usuario |
| `dashboard_view.py` | `/dashboard` | REDISENO: dashboard por area + principal con alertas |
| `clientes_view.py` | `/clientes` | Filtros avanzados, mapa, WhatsApp verificacion. ELIMINADO: exportar |
| `polizas_view.py` | `/polizas` | Filtros multiples, busqueda global, acciones lote |
| `pagos_view.py` | `/cobranza/pagos` | Vista master-detail, timeline, contado-a-cuotas como pestana |
| `pagos_temporales_view.py` | `/cobranza/autorizaciones` | UNIFICADO con panel autorizacion pagos y revision pagos |
| `revision_pagos_view.py` | (Unificado en `/cobranza/autorizaciones`) | ELIMINADO como vista separada |
| `tarjetas_view.py` | `/cobranza/cuentas` | REDISENO: 3 propuestas alternativas |
| `recibos_view.py` | `/cobranza/recibos` | Dashboard metricas + recibos electronicos |
| `cancelaciones_view.py` | `/cobranza/cancelaciones` | Graficas de tendencia |
| `contado_cuotas_view.py` | (Integrado en `/cobranza/pagos`) | MOVIDO: pestana dentro de Pagos |
| `promociones_view.py` | `/cobranza/promociones` | Sistema de reglas flexibles |
| `mensajes_cobranza_view.py` | `/cobranza/mensajes` | Multicanal, templates editables |
| `avisos_visita_view.py` | `/cobranza/rutas-visitas` | AMPLIADO: GPS, tracking tiempo real, rutas historicas |
| `cobranza_dashboard_view.py` | `/cobranza` | Mapa de calor, tendencias, ingresos dia/mes/ano |
| `cobradores_view.py` | `/cobranza/cobradores` | Dashboard por cobrador |
| `siniestros_view.py` | `/siniestros` | Separar logica, mapa, workflow, dashboard propio |
| `gruas_view.py` | `/gruas` | Mapa origen/destino, proveedores cercanos, alertas arribo |
| `endosos_view.py` | `/endosos` | Formulario dinamico, calculo auto costo cambio cobertura |
| `vendedores_view.py` | `/admin/empleados` | UNIFICADO: tabla de empleados con multiples roles |
| `coverages_view.py` | `/admin/coberturas` | Comparador, historial precios |
| `adjusters_view.py` | (Integrado en `/admin/empleados`) | UNIFICADO en empleados |
| `adjuster_shifts_view.py` | `/admin/guardias` | Calendario tipo Google |
| `renovaciones_view.py` | `/admin/renovaciones` | Funnel, asignacion. NOTA: se discutira a detalle |
| `tow_providers_view.py` | `/admin/proveedores-gruas` | Mapa zona cobertura |
| `admin_usuarios_view.py` | `/admin/usuarios` | Matriz permisos, auditoria, empleados multi-rol |
| (NUEVO) | `/autorizacion-polizas` | Panel revision polizas app movil |
| (NUEVO) | `/cobranza/autorizaciones` | Unifica pagos temporales + revision + autorizacion |
| (NUEVO) | `/cobranza/rutas-visitas` | Tracking tiempo real + rutas historicas + avisos |
| (NUEVO) | `/rrhh` | Recursos Humanos: panel personal, vacaciones, permisos |
| (NUEVO) | `/reportes` | Centro de reportes |
| (NUEVO) | `/notificaciones` | Centro de notificaciones |

## APENDICE B: RESUMEN DE DIALOGOS ACTUALES

| Dialogo | Archivo | Uso en web |
|---------|---------|-----------|
| `poliza_form_dialog.py` | Crear/Editar poliza | Wizard de 4 pasos en pagina completa |
| `poliza_details_dialog.py` | Ver detalle poliza | Pagina `/polizas/:folio` |
| `poliza_pagos_dialog.py` | Ver pagos de poliza | Tab en detalle de poliza |
| `poliza_pago_form_dialog.py` | Editar pago individual | Modal en tab de pagos |
| `restructurar_pagos_dialog.py` | Contado a cuotas | Modal con preview |
| `amplia_select_eligibility_dialog.py` | Elegibilidad AMPLIA | Panel en detalle poliza |
| `cliente_dialog.py` | Detalle de cliente | Pagina `/clientes/:id` |
| `cliente_form_dialog.py` | Crear/Editar cliente | Drawer lateral |
| `buscar_cliente_dialog.py` | Seleccionar cliente | Typeahead autocomplete |
| `incident_dialog.py` | Crear/Editar siniestro | Pagina completa |
| `incident_details.py` | Ver detalle siniestro | Pagina `/siniestros/:id` |
| `workshop_pass_dialog.py` | Pase de taller | Modal en detalle siniestro |
| `medical_pass_dialog.py` | Pase medico | Modal en detalle siniestro |
| `incident_satisfaction_survey_dialog.py` | Encuesta siniestro | Modal |
| `tow_service_dialog.py` | Crear servicio grua | Wizard con mapa |
| `tow_service_details.py` | Detalle servicio grua | Pagina `/gruas/:id` |
| `tow_satisfaction_survey_dialog.py` | Encuesta grua | Modal |
| `quote_providers_dialog.py` | Cotizar proveedores | Modal con lista |
| `tow_provider_form_dialog.py` | Crear/Editar proveedor | Modal |
| `vendedor_form_dialog.py` | Crear/Editar vendedor | Modal |
| `cobrador_form_dialog.py` | Crear/Editar cobrador | Modal |
| `coverage_form_dialog.py` | Crear/Editar cobertura | Modal |
| `adjuster_form_dialog.py` | Crear/Editar ajustador | Modal |
| `promocion_form_dialog.py` | Crear/Editar promocion | Modal con constructor reglas |
| `cancelacion_form_dialog.py` | Registrar cancelacion | Modal |
| `folios_discrepancia_dialog.py` | Folios sin pagos | Modal de alerta |
| `patch_notes_dialog.py` | Notas de version | Eliminar (usar changelog web) |
| `siga_dialog.py` | Consulta SIGA | Modal o integrar en detalle |
| `change_password_dialog.py` | Cambiar contrasena | Modal desde perfil |
| `image_crop_dialog.py` | Recortar imagen | Componente de upload web |
| `loading_dialog.py` | Indicador de carga | Spinner/skeleton web nativo |

## APENDICE C: COMPONENTES REUTILIZABLES ACTUALES

| Componente | Archivo | Equivalente web |
|-----------|---------|----------------|
| `clientes_search.py` | Buscador de clientes | `<SearchInput>` con debounce |
| `clientes_pagination.py` | Paginacion de clientes | `<Pagination>` generico |
| `polizas_search.py` | Buscador de polizas | `<SearchInput>` |
| `polizas_pagination.py` | Paginacion de polizas | `<Pagination>` |
| `siniestros_search.py` | Buscador de siniestros | `<SearchInput>` |
| `gruas_search.py` | Buscador de gruas | `<SearchInput>` |
| `endosos_pagination.py` | Paginacion de endosos | `<Pagination>` |
| `search_line_edit.py` | Input de busqueda base | `<SearchInput>` base |
| `pagination.py` | Paginacion base | `<Pagination>` base |
| `loading_dialog.py` | Dialogo de carga | `<LoadingSkeleton>` |
| `styled_message_box.py` | MessageBox estilizado | Toast notification (sonner) |
| `filter_badge_widget.py` | Badge de filtro activo | `<FilterBadge>` chip |
| `filter_badges_container.py` | Contenedor de badges | `<FilterBar>` |
| `dashboard_cards.py` | Tarjetas de metricas | `<StatCard>` |
| `cobrador_section.py` | Seccion de cobrador | Componente de dashboard |
| `pagos_section.py` | Seccion de pagos | Componente de dashboard |
| `resumen_section.py` | Seccion de resumen | Componente de dashboard |
| `payment_widget.py` | Widget de pago | `<PaymentCard>` |

---

> Documento generado el 14/02/2026. Basado en el analisis de todos los archivos de views/, views/dialogs/, views/components/ y views/widgets/ del proyecto pqtCreacion.
> Total de vistas documentadas: 25 existentes + 5 nuevas propuestas + 3 apps moviles.
> Total de dialogos documentados: 30.
> Total de componentes reutilizables: 18.
