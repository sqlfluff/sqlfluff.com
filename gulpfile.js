"use strict";

// Load plugins
const browsersync = require("browser-sync").create();
const del = require("del");
const gulp = require("gulp");
const merge = require("merge-stream");
const nunjucks = require('gulp-nunjucks');

// BrowserSync
function browserSync(done) {
  browsersync.init({
    server: {
      baseDir: "./dist/",
      // Assume html extension if not specified
      serveStaticOptions: {
        extensions: ["html"]
      }
    },
    port: 3000
  });
  done();
}

// BrowserSync reload
function compile(done) {
  // compile html
  gulp.src('./src/templates/*.html')
		.pipe(nunjucks.compile())
    .pipe(gulp.dest('./dist'))
  // copy css, js and images
  gulp.src('./src/css/**/*')
    .pipe(gulp.dest('./dist/css'));
  gulp.src('./src/js/**/*')
    .pipe(gulp.dest('./dist/js'));
  gulp.src('./src/images/**/*')
    .pipe(gulp.dest('./dist/images'));
  done();
}

// BrowserSync reload
function browserSyncReload(done) {
  compile(function(){});
  browsersync.reload();
  done();
}

// Clean vendor
function cleanVendor() {
  return del(["./dist/vendor/"]);
}

// Clean proj (not vendor)
function cleanProj() {
  return del(["./dist/", "!./dist/vendor/"]);
}

// Bring third party dependencies from node_modules into vendor directory
function modules() {
  // Bootstrap
  var bootstrap = gulp.src([
      './node_modules/bootstrap/dist/**/*.min.css',
      './node_modules/bootstrap/dist/**/*.min.js'])
    .pipe(gulp.dest('./dist/vendor/bootstrap'));
  // jQuery
  var jquery = gulp.src([
      './node_modules/jquery/dist/*.min.js',
      './node_modules/jquery/dist/*.min.map',
      '!./node_modules/jquery/dist/core.js'
    ])
    .pipe(gulp.dest('./dist/vendor/jquery'));
  // fontawesome
  var fontawesome_css = gulp.src([
      './node_modules/@fortawesome/fontawesome-free/css/*.min.css',
    ])
    .pipe(gulp.dest('./dist/vendor/fontawesome/css'));
  var fontawesome_fonts = gulp.src([
      './node_modules/@fortawesome/fontawesome-free/webfonts/*',
    ])
    .pipe(gulp.dest('./dist/vendor/fontawesome/webfonts'));
  var fontawesome_js = gulp.src([
      './node_modules/@fortawesome/fontawesome-free/js/*.min.js',
    ])
    .pipe(gulp.dest('./dist/vendor/fontawesome/js'));
  return merge(
    bootstrap, jquery, fontawesome_css, fontawesome_fonts, fontawesome_js);
}

// Watch files
function watchFiles() {
  // Source files
  gulp.watch("./src/**/*.css", browserSyncReload);
  gulp.watch("./src/**/*.js", browserSyncReload);
  gulp.watch("./src/**/*.html", browserSyncReload);
  // Image Files
  gulp.watch("./src/**/*.png", browserSyncReload);
  gulp.watch("./src/**/*.jpg", browserSyncReload);
}

// Define complex tasks
const vendor = gulp.series(cleanVendor, modules);
const build = gulp.parallel(vendor, gulp.series(cleanProj, compile));
const watch = gulp.series(build, gulp.parallel(watchFiles, browserSync));

// Export tasks
exports.clean = gulp.parallel(cleanVendor, cleanProj);
exports.vendor = vendor;
exports.build = build;
exports.watch = watch;
exports.default = build;
