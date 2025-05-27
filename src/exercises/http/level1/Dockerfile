FROM php:7.4-apache

# Install required PHP extensions
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Copy the application files
COPY src/ /var/www/html/

# Set permissions
RUN chown -R www-data:www-data /var/www/html/

# Expose the web server port
EXPOSE 80

# Start Apache in foreground mode
CMD ["apachectl", "-D", "FOREGROUND"]
