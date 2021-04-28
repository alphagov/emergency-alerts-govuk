// file-transformer.js
'use strict';

module.exports = {
  process(src, filename) {
    console.log('In file-transformer.process');
    console.log(src, filename);

    return src;
  }
};
