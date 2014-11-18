/*global module:false*/
module.exports = function(grunt) {
    'use strict';

    //displays the elapsed time for the execution of grunt tasks
    require('time-grunt')(grunt);

  /**
    * Project initial configuration
    */
  grunt.initConfig({
    // Metadata.
    pkg: grunt.file.readJSON('package.json'),
    banner: '/*! <%= pkg.title || pkg.name %> - v<%= pkg.version %> - ' +
      '<%= grunt.template.today("yyyy-mm-dd") %>\n' +
      '<%= pkg.homepage ? "* " + pkg.homepage + "\\n" : "" %>' +
      '* Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author.name %>;' +
      ' Licensed <%= _.pluck(pkg.licenses, "type").join(", ") %> */\n',
    
    // Task configuration.
    // Concatenate
    concat: {
      options: {
          banner: "/* CSS files concatenated |  <%= grunt.template.today('dd-mm-yyyy') %> */\n",
      },
      target: {
        src: ["app/static/css/*.css"],
        dest: "app/static/cssall/main.css"
            }
        },
      jshint: {
        options: {
          curly: true,
          eqeqeq: true,
          immed: true,
          latedef: true,
          newcap: true,
          noarg: true,
          sub: true,
          undef: true,
          unused: true,
          boss: true,
          eqnull: true,
          browser: true,
          globals: {
            jQuery: true
          }
      },
      gruntfile: {
        src: 'Gruntfile.js'
      }
    },
    sass: {                              // Task
      dist: {                            // Target
        files: {                         // Dictionary of files
          'app/static/css/main.css': 'app/static/scss/main.scss'      // 'destination': 'source'
        }
      },
      dev: {                             // Another target
        options: {                       // Target options
          style: 'expanded'
        },
        files: {
          'app/static/css/main.css': 'app/static/scss/main.scss'
        }
      }
    },
    watch: {
      sass: {
        files: ['Gruntfile.js', './app/static/scss/*'],
        tasks: ['default']
      }
    }
  });

  // These plugins provide necessary tasks.
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jasmine');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-sass');

  // Default task.
  //grunt.registerTask('default', ['jshint', 'qunit', 'concat', 'uglify', 'sass']);
  grunt.registerTask('default', ['sass', 'concat']);

};