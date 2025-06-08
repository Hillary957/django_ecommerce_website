

from django import forms

class MpesaForm(forms.Form):
    phone_number = forms.CharField(label='Phone Number', max_length=15)
    amount = forms.IntegerField(label='Amount', min_value=1)

    def clean_phone_number(self): 
        phone = self.cleaned_data.get("phone_number")

        if not phone:
            raise forms.ValidationError("Phone number is required")

        phone = phone.replace(" ", "")  # Remove spaces if user added any

        if phone.startswith('07') or phone.startswith('01'):
            return '254' + phone[1:]
        elif phone.startswith('+254'):
            return phone[1:]  # removes the '+' only
        elif phone.startswith('254'):
            return phone
        else:
            raise forms.ValidationError("Invalid phone number format. Use +254, 07, or 01")














# from django import forms

# class MpesaForm(forms.Form):
#     phone_number = forms.CharField(label='Phone Number', max_length=15)
#     amount = forms.IntegerField(label='Amount', min_value=1)

#     def clean_phone_number(self): 
#         phone = self.cleaned_data.get("phone_number")

#         if not phone:
#             if phone.startswith('07') or phone.startswith('01'):
#                 return '254'+ phone[1:]
#             elif phone.startswith('+254'):
#                  return phone[1:]
#             elif phone.startswith('254'):
#                 return phone
#             else:
#                raise ValueError("Invalid phone number format")       
#         return phone
    
       
        
        
       
