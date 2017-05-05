# XBlock SDK Workbench compatible mixin and scenarios

## To run VideoXBlock workbench scenarios

1. Clone [XBlock SDK](https://github.com/edx/xblock-sdk) in parent directory:

   ```bash
   git clone git@github.com:edx/xblock-sdk.git -b v0.1.3 ../xblock-sdk
   ```

1. Make sure VideoXBlock is installed into your environment:

   ```bash
   make dev-install
   ```

1. Run Workbench:

   ```bash
   ../xblock-sdk/manage.py runserver
   ```

1. Go to <http://localhost:8000/> in your browser.
