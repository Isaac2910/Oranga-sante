Projet Oranga Sante


mail en dev:

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False  # Maildev n'a pas besoin de TLS
EMAIL_HOST_USER = ''  # Laissez vide, Maildev ne nécessite pas d'authentification
EMAIL_HOST_PASSWORD = ''  # Pas d'authentification nécessaire
DEFAULT_FROM_EMAIL = 'webmaster@localhost'
