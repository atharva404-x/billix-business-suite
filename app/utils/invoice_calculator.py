
from typing import List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class InvoiceItemCalculation:
    product_id: str
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal
    gst_rate: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    total: Decimal


@dataclass
class InvoiceCalculationResult:
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    cgst_amount: Optional[Decimal]
    sgst_amount: Optional[Decimal]
    igst_amount: Optional[Decimal]
    total_tax: Decimal
    round_off: Decimal
    grand_total: Decimal
    items: List[InvoiceItemCalculation]


class InvoiceCalculator:
    @staticmethod
    def _round(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_item(
        quantity: Decimal,
        unit_price: Decimal,
        discount: Optional[Decimal] = None,
        gst_rate: Optional[Decimal] = None,
    ) -> Tuple[InvoiceItemCalculation, Decimal]:
        discount = discount or Decimal("0.00")
        gst_rate = gst_rate or Decimal("0.00")
        
        line_total = quantity * unit_price
        taxable_amount = line_total - discount
        tax_amount = (taxable_amount * gst_rate) / Decimal("100") if gst_rate > 0 else Decimal("0.00")
        total = taxable_amount + tax_amount
        
        item = InvoiceItemCalculation(
            product_id="",
            quantity=quantity,
            unit_price=unit_price,
            discount=discount,
            gst_rate=gst_rate,
            taxable_amount=taxable_amount,
            tax_amount=tax_amount,
            total=total,
        )
        
        return item, tax_amount

    @staticmethod
    def calculate_invoice(
        items_data: List[dict],
        discount_amount: Optional[Decimal] = None,
        business_state: Optional[str] = None,
        customer_state: Optional[str] = None,
    ) -> InvoiceCalculationResult:
        discount_amount = discount_amount or Decimal("0.00")
        subtotal = Decimal("0.00")
        total_tax = Decimal("0.00")
        calculated_items: List[InvoiceItemCalculation] = []
        
        for item_data in items_data:
            item_dict, item_tax = InvoiceCalculator.calculate_item(
                quantity=Decimal(str(item_data["quantity"])),
                unit_price=Decimal(str(item_data["unit_price"])),
                discount=Decimal(str(item_data.get("discount", "0.00"))),
                gst_rate=Decimal(str(item_data.get("gst_rate", "0.00"))),
            )
            item_dict.product_id = str(item_data["product_id"])
            calculated_items.append(item_dict)
            subtotal += item_dict.taxable_amount + item_dict.discount
            total_tax += item_tax
        
        taxable_amount = subtotal - discount_amount
        
        # Determine GST type based on business and customer states
        cgst_amount: Optional[Decimal] = None
        sgst_amount: Optional[Decimal] = None
        igst_amount: Optional[Decimal] = None
        
        if business_state and customer_state and business_state == customer_state:
            cgst_amount = total_tax / Decimal("2")
            sgst_amount = total_tax / Decimal("2")
        else:
            igst_amount = total_tax
        
        # Calculate grand total and round off
        total_before_round = taxable_amount + total_tax
        grand_total = InvoiceCalculator._round(total_before_round)
        round_off = grand_total - total_before_round
        
        return InvoiceCalculationResult(
            subtotal=subtotal,
            discount_amount=discount_amount,
            taxable_amount=taxable_amount,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            igst_amount=igst_amount,
            total_tax=total_tax,
            round_off=round_off,
            grand_total=grand_total,
            items=calculated_items,
        )

