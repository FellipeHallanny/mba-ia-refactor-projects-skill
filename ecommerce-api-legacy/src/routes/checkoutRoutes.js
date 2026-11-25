const express = require('express');
const CheckoutController = require('../controllers/CheckoutController');

const router = express.Router();
router.post('/checkout', CheckoutController.processCheckout);

module.exports = router;
