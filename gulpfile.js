'use strict';

const path = require('path');

const { src, pipe, dest, series, parallel, watch } = require('gulp');
const Fiber = require('fibers');

const plugins = {}
plugins.sass = require('gulp-sass');
plugins.gulpStylelint = require('gulp-stylelint');
plugins.gulpif = require('gulp-if');
plugins.postcss = require('gulp-postcss');

const paths = {
  src: 'src/assets/',
  node_modules: 'node_modules/',
  dist: 'dist/alerts/assets/',
  govuk_frontend: 'node_modules/govuk-frontend/'
};

plugins.sass.compiler = require('sass');

const copy = {
  govuk_frontend: {
    fonts: () => {
      return src(paths.govuk_frontend + 'govuk/assets/fonts/**/*')
        .pipe(dest(paths.dist + 'fonts/'));
    },
    images: () => {
      return src(paths.govuk_frontend + 'govuk/assets/images/**/*')
        .pipe(dest(paths.dist + 'images/'));
    }
  },
  html5shiv: () => {
    return src(paths.node_modules + 'html5shiv/dist/*.min.js')
      .pipe(dest(paths.dist + 'javascripts/vendor/html5shiv/'));
  }
};

const scss = {
  lint: () => {
    return src(paths.src + 'stylesheets/*.scss')
      .pipe(plugins.gulpStylelint({
        failAfterError: true,
        reporters: [
          {formatter: 'string', console: true}
        ]
      }));
  },
  compile: () => {
    return src(paths.src + 'stylesheets/**/*.scss')
      .pipe(plugins.sass(
        {
          fiber: Fiber,
          includePaths: [paths.govuk_frontend],
          outputStyle: 'compressed'
        })
        .on('error', plugins.sass.logError))
        .pipe(plugins.gulpif(
          (file) => {
            return path.basename(file.path) === 'main-ie8.css';
          },
          plugins.postcss([require('oldie')()])
        ))
      .pipe(dest(paths.dist + 'stylesheets/'));
  }
};

const defaultTask = parallel(
  parallel(
    copy.govuk_frontend.fonts,
    copy.govuk_frontend.images,
    copy.html5shiv,
    scss.lint,
    scss.compile
  )
);

exports.default = defaultTask;
