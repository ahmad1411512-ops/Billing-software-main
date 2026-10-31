from io import BytesIO
from decimal import Decimal, ROUND_HALF_UP
from django.template.loader import get_template

_ONES = [
    '', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
    'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
    'Seventeen', 'Eighteen', 'Nineteen',
]
_TENS = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']


def _words_under_thousand(n):
    n = int(n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        return f'{_TENS[tens]} {_ONES[ones]}'.strip()
    hundreds, rest = divmod(n, 100)
    if rest:
        return f'{_ONES[hundreds]} Hundred {_words_under_thousand(rest)}'
    return f'{_ONES[hundreds]} Hundred'


def amount_in_words(amount):
    """Convert a rupee amount to English words, e.g. Five Thousand Five Hundred Only."""
    value = Decimal(str(amount or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rupees = int(value)
    paisa = int((value - Decimal(rupees)) * 100)

    if rupees == 0 and paisa == 0:
        return 'Zero Only'

    parts = []
    crore, rem = divmod(rupees, 10000000)
    lakh, rem = divmod(rem, 100000)
    thousand, rem = divmod(rem, 1000)
    if crore:
        parts.append(f'{_words_under_thousand(crore)} Crore')
    if lakh:
        parts.append(f'{_words_under_thousand(lakh)} Lakh')
    if thousand:
        parts.append(f'{_words_under_thousand(thousand)} Thousand')
    if rem:
        parts.append(_words_under_thousand(rem))

    words = ' '.join(parts) if parts else 'Zero'
    if paisa:
        words = f'{words} and {_words_under_thousand(paisa)} Paisa'
    return f'{words} Only'


def short_invoice_no(invoice_number):
    last = str(invoice_number or '').split('-')[-1]
    try:
        return str(int(last))
    except (TypeError, ValueError):
        return str(invoice_number or '')

def render_to_pdf(template_src, context_dict={}):
    try:
        from xhtml2pdf import pisa
    except ImportError as exc:
        raise RuntimeError(
            "PDF generation requires xhtml2pdf. Install it with: pip install xhtml2pdf"
        ) from exc

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None
