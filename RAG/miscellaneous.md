## LayuotLM

The original idea behind the LayoutLM family is essentially:
Don't just understand what the words say.
Understand where those words occur on the document

Eg.
-------------------------------------------------
ACME CORPORATION

Invoice Number:                   INV-9281
Invoice Date:                     24 Oct 2026

Bill To:                          Total:
Prakhar Singh                     ₹18,500

-------------------------------------------------
Item              Qty            Price
GPU Rental         2             ₹15,000
Storage            1              ₹3,500
-------------------------------------------------
These are not just words

Before LayoutLM, models usually read documents like a plain text file or treated them purely as images
LayoutLM introduced a technique that fuses three streams of data simultaneously into a single transformer architecture

1. Text (The Words): What the words actually say (handled via standard NLP token embeddings, much like BERT).

2. Vision (The Appearance): The visual features of the document image (like font size, bolding, or layout blocks).

3. Spatial Layout (The Coordinates): The exact 2D bounding-box coordinates (x_0, y_0, x_1, y_1) of every word on the page, scaled from 0 to 1000.