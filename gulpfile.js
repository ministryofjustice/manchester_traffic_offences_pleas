var gulp = require('gulp'),
    del = require('del'),
    imagemin = require('gulp-imagemin'),
    concat = require('gulp-concat'),
    stylish = require('jshint-stylish'),
    jshint = require('gulp-jshint'),
    runSequence = require('run-sequence'),
    vinylPaths = require('vinyl-paths'),
    jasmine = require('gulp-jasmine'),
    karmaServer = require('karma').Server,
    uglify = require('gulp-uglify'),
    sourcemaps = require('gulp-sourcemaps'),
    sass = require('gulp-sass'),
    file = require('gulp-file'),
    include = require('gulp-include');

var paths = {
  dest_dir: 'make_a_plea/assets/',
  src_dir: 'make_a_plea/assets-src/',
  styles: [
    'make_a_plea/assets-src/stylesheets/**/*.scss',
    'node_modules/govuk_frontend_toolkit/stylesheets/**/*.scss'
  ],
  scripts: 'make_a_plea/assets-src/javascripts/application.js',
  vendor_scripts: 'make_a_plea/assets-src/javascripts/vendor/**/*.js',
  test_scripts: 'make_a_plea/assets-src/tests/**/*.js',
  images: 'make_a_plea/assets-src/images/**/*'
};

// clean out assets folder
gulp.task('clean', function() {
  return gulp
    .src(paths.dest_dir, {read: false})
    .pipe(vinylPaths(del));
});

// Create healthcheck.txt
gulp.task('healthcheck', function() {
  return file('healthcheck.txt', "OK", {src: true})
    .pipe(gulp.dest(paths.dest_dir));
});

// compile scss
gulp.task('sass', function() {
  gulp
    .src(paths.styles)
    .pipe(sourcemaps.init())
    .pipe(sass({
      outputStyle: 'compressed',
      includePaths: [
        'node_modules/govuk_frontend_toolkit/',
        'node_modules/govuk_frontend_toolkit/stylesheets/',
        'make_a_plea/assets-src/stylesheets/'
      ]
    }))
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest(paths.dest_dir + 'stylesheets'));
});

// default js task
gulp.task('js', function() {
  // create concatenated main js file
  gulp
    .src(paths.scripts)
    .pipe(include())
      .on('error', console.log)
    .pipe(sourcemaps.init())
    .pipe(concat('application.js'))
    .pipe(uglify())
    .pipe(sourcemaps.write('../maps'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts'));

  // copy static vendor files
  gulp
    .src(paths.vendor_scripts)
    .pipe(gulp.dest(paths.dest_dir + 'javascripts/vendor'));
});

// jshint
gulp.task('lint', function() {
  var files = paths.scripts.slice(0);

  gulp
    .src(files)
    .pipe(jshint())
    .pipe(jshint.reporter(stylish));
});

// JS Tests
gulp.task('test', function (done) {
  new karmaServer({
    configFile: __dirname + '/karma.conf.js'
  }, function() {
    done();
  }).start();
});

// optimise images
gulp.task('images', function() {
  gulp
    .src(paths.images)
    .pipe(imagemin({optimizationLevel: 5}))
    .pipe(gulp.dest(paths.dest_dir + 'images'));
});

// setup watches
gulp.task('watch', function() {
  gulp.watch(paths.styles, ['sass']);
  gulp.watch(paths.src_dir + 'javascripts/**/*.js', ['lint', 'js']);
  gulp.watch(paths.images, ['images']);
});

// setup default tasks
gulp.task('default', ['build']);
// run build
gulp.task('build', function() {
  runSequence('clean', 'healthcheck', ['lint', 'js', 'images', 'sass']);
});
