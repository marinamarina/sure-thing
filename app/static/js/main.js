require.config({
    baseUrl: "http://localhost:5000/static/js/",
    paths: {
        'pubsub': 'vendor/eventEmitter',
        'headroom1': 'vendor/headroom.min',
        'headroom' : 'vendor/jQuery.headroom.min',
        'classie' : 'vendor/classie',
        'bootstrap' : 'vendor/bootstrap.min',
        'cookie': 'vendor/jquery.cookie',
        'app' : 'views/app'
    }
});

require(['app', 'classie'], function(app, classie) {
  app.init(classie);
});