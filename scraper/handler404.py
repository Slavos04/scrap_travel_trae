from django.shortcuts import render

def handler404(request, exception):
    """
    Custom 404 error handler
    """
    return render(request, 'scraper/404.html', status=404)

def handler500(request, *args, **argv):
    """
    Custom 500 error handler
    """
    return render(request, 'scraper/500.html', status=500)