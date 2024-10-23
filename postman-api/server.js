const express = require('express');
const mongoose = require('mongoose');

const app = express();
const PORT = 3000;

mongoose.connect('mongodb://localhost:27017/tfm', { useNewUrlParser: true, useUnifiedTopology: true });

const statusSchema = new mongoose.Schema({}, { collection: 'status_01' });
const Status = mongoose.model('Status', statusSchema);

app.get('/status_01', async (req, res) => {
	  try {
		      const data = await Status.find({});
		      res.json(data);
		    } catch (err) {
			        res.status(500).json({ error: err.message });
			      }
});

app.listen(PORT, () => {
	  console.log(`Server running on http://localhost:${PORT}`);
});

