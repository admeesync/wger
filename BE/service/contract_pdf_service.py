from fpdf import FPDF

from models.contract import Contract


def generate_contract_pdf(contract: Contract, gym_name: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, gym_name, ln=True)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Membership Contract', ln=True)
    pdf.ln(6)

    member = contract.member
    rows = [
        ('Member', member.get_full_name() if member else ''),
        ('Email', member.email if member else ''),
        ('Contract Type', contract.contract_type.name if contract.contract_type else '-'),
        ('Options', ', '.join(o.name for o in contract.options) or '-'),
        ('Amount', f'Rs. {contract.amount}'),
        ('Start Date', str(contract.date_start)),
        ('End Date', str(contract.date_end) if contract.date_end else 'No end date'),
    ]
    pdf.set_font('Helvetica', '', 11)
    for label, value in rows:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(45, 8, label)
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 8, str(value), ln=True)

    if contract.note:
        pdf.ln(4)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 8, 'Notes', ln=True)
        pdf.set_font('Helvetica', '', 11)
        pdf.multi_cell(0, 7, contract.note)

    return bytes(pdf.output())
