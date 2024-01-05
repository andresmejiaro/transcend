FROM nginx:alpine

# Remove the default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Set the working directory
WORKDIR /usr/share/nginx/html

# Copy the frontend files into the container
# COPY Front /usr/share/nginx/html

# Copy the custom Nginx configuration
COPY nginx/conf/default.conf /etc/nginx/conf.d/

COPY nginx/setup.sh /setup.sh
RUN chmod +x /setup.sh

# Expose port 3000
EXPOSE 3000

# Command to start Nginx
CMD ["/setup.sh"]