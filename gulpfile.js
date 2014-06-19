var gulp = require('gulp'),
    plugins = require('gulp-load-plugins')(),
    stylish = require('jshint-stylish'),
    runSequence = require('run-sequence');

var paths = {
  dest_dir: 'manchester_traffic_offences/assets/',
  src_dir: 'manchester_traffic_offences/assets-src/',
  styles: 'manchester_traffic_offences/assets-src/stylesheets/**/*.scss',
  templates: 'manchester_traffic_offences/assets-src/javascripts/templates/*.hbs',
  scripts: [
    // vendor scripts
    'manchester_traffic_offences/assets-src/vendor/lodash/dist/lodash.min.js',
    'manchester_traffic_offences/assets-src/vendor/jquery-details/jquery.details.js',
    'manchester_traffic_offences/assets-src/vendor/handlebars/handlebars.js',
    // templates
    'manchester_traffic_offences/assets-src/javascripts/templates.js',
    // CLA
    'manchester_traffic_offences/assets-src/javascripts/moj.Helpers.js',
    'manchester_traffic_offences/assets-src/javascripts/modules/*'
  ],
  vendor_scripts: 'manchester_traffic_offences/assets-src/javascripts/vendor/*',
  images: 'manchester_traffic_offences/assets-src/images/**/*'
};

// clean out assets folder
gulp.task('clean', function() {
  return gulp
    .src(paths.dest_dir, {read: false})
    .pipe(plugins.clean());
});

// compile scss
gulp.task('sass', function() {
  gulp
    .src(paths.styles)
    .pipe(plugins.rubySass({
      loadPath: 'node_modules/govuk_frontend_toolkit/' // add node module toolkit path
    }))
    .pipe(gulp.dest(paths.dest_dir + 'stylesheets'));
});

// js templates
gulp.task('templates', function(){
  gulp.src(paths.templates)
    .pipe(plugins.handlebars())
    .pipe(plugins.defineModule('plain'))
    .pipe(plugins.declare({
      namespace: 'CLA.templates'
    }))
    .pipe(plugins.concat('templates.js'))
    .pipe(gulp.dest(paths.src_dir + 'javascripts'));
});

// default js task
gulp.task('js', ['templates'], function() {
  var prod = paths.scripts.slice(0);

  // ignore debug files
  prod.push('!' + paths.src_dir + '**/*debug*');
  // create concatinated js file
  gulp
    .src(prod)
    .pipe(plugins.concat('cla.main.js'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts'));
  // copy static vendor files
  gulp
    .src(paths.vendor_scripts)
    .pipe(gulp.dest(paths.dest_dir + 'javascripts/vendor'));
  // create debug js file
  gulp
    .src(paths.src_dir + 'javascripts/**/*debug*')
    .pipe(plugins.concat('cla.debug.js'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts/'));
});

// jshint js code
gulp.task('lint', function() {
  var files = paths.scripts.slice(0);

  // files to ignore from linting
  files.push('!manchester_traffic_offences/assets-src/vendor/**');
  files.push('!manchester_traffic_offences/assets-src/javascripts/vendor/**');
  files.push('!manchester_traffic_offences/assets-src/javascripts/templates.js');

  gulp
    .src(files)
    .pipe(plugins.jshint())
    .pipe(plugins.jshint.reporter(stylish));
});

// optimise images
gulp.task('images', function() {
  gulp
    .src(paths.images)
    .pipe(plugins.imagemin({optimizationLevel: 5}))
    .pipe(gulp.dest(paths.dest_dir + 'images'));
});

// setup watches
gulp.task('watch', function() {
  gulp.watch(paths.styles, ['sass']);
  gulp.watch(paths.src_dir + 'javascripts/**/*', ['lint', 'js']);
  gulp.watch(paths.images, ['images']);
});

// setup default tasks
gulp.task('default', ['build']);
// run build
gulp.task('build', function() {
  runSequence('clean', ['lint', 'templates', 'js', 'images', 'sass']);
});