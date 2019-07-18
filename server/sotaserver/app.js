var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var apiRouter = require('./routes/api');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', apiRouter);

app.use(function(req, res, next) {
  res.status(500);
  res.send();
});

app.use(function(err, req, res, next) {
  // render the error page
  res.status(500);
  res.send();
});

module.exports = app;
