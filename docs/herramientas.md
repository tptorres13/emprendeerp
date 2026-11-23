# Herramientas que usa el proyecto (explicado sin tecnicismos)

## Lo que construye el sistema

| Herramienta | Para qué sirve |
|---|---|
| **Python** | El idioma en el que está escrito el programa. |
| **Django** | El "esqueleto" del sistema: ya trae resueltas muchas cosas comunes (usuarios, páginas, seguridad), así no se arma todo de cero. |
| **PostgreSQL** | La base de datos: donde se guarda toda la información (productos, ventas, clientes). Es como un Excel gigante, ordenado y muy seguro. |
| **HTML + Tailwind CSS** | Lo que hace que las pantallas se vean lindas y se adapten al celular. |
| **HTMX** | Permite que partes de la pantalla se actualicen sin recargar toda la página, para que se sienta rápido. |
| **django-allauth** | Se encarga de registrarse, entrar, recuperar la contraseña y bloquear a quien intenta adivinar claves. |
| **Argon2** | Guarda las contraseñas cifradas, para que nadie pueda leerlas, ni siquiera nosotros. |
| **Gunicorn y Whitenoise** | Los que "sirven" el sistema en internet cuando está publicado. |

## Lo que lo mantiene ordenado y seguro

| Herramienta | Para qué sirve |
|---|---|
| **pytest** | Corre 47 pruebas automáticas que verifican que todo funcione, por ejemplo que un negocio nunca vea los datos de otro. |
| **Ruff** | Revisa que el código esté prolijo y sin errores comunes, como un corrector ortográfico. |
| **pre-commit** | Corre esa revisión solo, antes de guardar cada cambio. |
| **GitHub Actions (CI)** | Cada vez que se sube un cambio, repite todas las pruebas solo. Si algo se rompe, avisa. |
| **uv** | Administra las librerías que usa el proyecto y deja todo con versiones fijas, para que funcione igual en cualquier computadora. |

## Lo que lo hace fácil de instalar y publicar

| Herramienta | Para qué sirve |
|---|---|
| **Docker y Docker Compose** | Empaquetan el sistema con todo lo que necesita. Con un solo comando se levanta igual en cualquier computadora o servidor. |
| **Mailpit** | Una "casilla de mail falsa" para ver los emails que manda el sistema (como el de recuperar contraseña) sin enviarlos de verdad. |
| **Railway, Render o un VPS** | Los servicios donde se publicaría el sistema en internet. Todavía no elegimos ninguno. |
| **GitHub** | Donde se guarda el código con todo su historial, y la copia de resguardo del proyecto. |

## Qué pasa cuando entrás al sistema

1. Te registrás con tu nombre, email y contraseña.
2. Un asistente de 3 pasos te pregunta el nombre del negocio, el rubro, la situación frente a ARCA y la moneda.
3. Te sugiere categorías según el rubro (por ejemplo, "Velas y aromas" para deco).
4. Entrás a tu inicio. Cada negocio ve solo sus propios datos.
