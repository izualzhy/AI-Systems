#!/usr/bin/env python
# coding=utf-8

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os

OUTPUT_DIR = "pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_pdf(serial_number: int):
    filename = f"gen_{serial_number:03d}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # PDF 内容
    c.setFont("Helvetica", 20)
    c.drawString(100, height - 150, f"Serial Number: {serial_number}")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 200, f"Generated at: {datetime.now()}")

    c.showPage()
    c.save()

    print(f"Generated: {filepath}")

if __name__ == "__main__":
    for i in range(1, 601):
        generate_pdf(i)
