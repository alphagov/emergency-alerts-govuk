'use strict';

const { src, pipe, dest, series, parallel, watch } = require('gulp');
const Fiber = require('fibers');

const plugins = {}
plugins.sass = require('gulp-sass');
plugins.gulpStylelint = require('gulp-stylelint');

const paths = {
  src: 'src/assets/',
  dist: 'dist/assets/',
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
          includePaths: [paths.govuk_frontend]
        })
        .on('error', plugins.sass.logError))
      .pipe(dest(paths.dist + 'stylesheets/'));
  }
};

const defaultTask = parallel(
  parallel(
    copy.govuk_frontend.fonts,
    copy.govuk_frontend.images,
    scss.lint,
    scss.compile
  )
);

exports.default = defaultTask;
