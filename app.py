from src import create_app

app = create_app(config_name='config.DevelopmentConfig')

if __name__ == '__main__':
    app.run()