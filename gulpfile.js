var gulp = require('gulp'),
    plugins = require('gulp-load-plugins')(),
    del = require('del'),
    stylish = require('jshint-stylish'),
    runSequence = require('run-sequence'),
    vinylPaths = require('vinyl-paths');

var paths = {
  dest_dir: 'manchester_traffic_offences/assets/',
  src_dir: 'manchester_traffic_offences/assets-src/',
  styles: ['manchester_traffic_offences/assets-src/stylesheets/main.scss',
           'node_modules/govuk_frontend_toolkit/govuk_frontend_toolkit/stylesheets/**/*.scss'],
  scripts: [
    // vendor scripts
    'manchester_traffic_offences/assets-src/vendor/jquery-details/jquery.details.js',
    // Application
    'manchester_traffic_offences/assets-src/javascripts/application.js',
  ],
  vendor_scripts: 'manchester_traffic_offences/assets-src/javascripts/vendor/*',
  govuk_scripts: 'node_modules/govuk_frontend_toolkit/govuk_frontend_toolkit/javascripts/**/*.js',
  images: 'manchester_traffic_offences/assets-src/images/**/*'
};

// clean out assets folder
gulp.task('clean', function() {
  return gulp
    .src(paths.dest_dir, {read: false})
    .pipe(vinylPaths(del));
});

// compile scss
gulp.task('sass', function() {
  gulp
    .src(paths.styles)
    .pipe(plugins.rubySass({
      loadPath: ['node_modules/govuk_frontend_toolkit/',
                 'manchester_traffic_offences/assets-src/stylesheets/']
    }))
    .pipe(gulp.dest(paths.dest_dir + 'stylesheets'));
});

// default js task
gulp.task('js', function() {
  var prod = paths.scripts.slice(0);

  // ignore debug files
  prod.push('!' + paths.src_dir + '**/*debug*');

  // create concatenated js file
  gulp
    .src(prod)
    .pipe(plugins.concat('application.js'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts'));

  // copy static vendor files
  gulp
    .src(paths.vendor_scripts)
    .pipe(gulp.dest(paths.dest_dir + 'javascripts/vendor'));

  //
  gulp
    .src(paths.govuk_scripts)
    .pipe(plugins.concat('govuk.js'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts'))

  // create debug js file
  gulp
    .src(paths.src_dir + 'javascripts/**/*debug*')
    .pipe(plugins.concat('debug.js'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts/'));
});

// jshint js code
gulp.task('lint', function() {
  var files = paths.scripts.slice(0);

  // files to ignore from linting
  files.push('!manchester_traffic_offences/assets-src/vendor/**');
  files.push('!manchester_traffic_offences/assets-src/javascripts/vendor/**');
  files.push('!node_modules/**');

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
  runSequence('clean', ['lint', 'js', 'images', 'sass']);
});
