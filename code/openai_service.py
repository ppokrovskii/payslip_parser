import os
import re
import logging
from openai import AzureOpenAI
from pydantic import BaseModel, ValidationError

class PayslipInfo(BaseModel):
    category: str
    amount: str
    currency: str
    date: str  # Expected to be in MMDD format

class OpenAIService:
    def __init__(self):
        """
        Initialize the OpenAIService with Azure OpenAI API credentials.
        """
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    def get_category_amount_ccy_and_date(self, text: str) -> PayslipInfo:
        """
        Extracts the category, amount, currency, and date from the payslip text.
        :param text: The text extracted from the payslip.
        :return: A PayslipInfo object containing the category, amount, currency, and date.
        """
        prompt = (
        "Given the following payslip text, extract the category (one of: hotel, taxi, food, other), "
        "amount (without rounding, keep the original value), currency, and date in MMDD format. "
        "don't make any assumptions, if data is not there or not clear, use 'other' category, or None for other fields. "
        "If both 'hotel' and 'food' categories seem applicable (e.g., in phrases like 'hotel bar' or 'hotel restaurant'), "
        "prioritize 'food' over 'hotel'. Use the provided function to return the response "
        "in the expected format.\n\n"
        f"Payslip Text:\n{text}\n\n"
        ) 
        


        # Define the function tool
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "store_payslip_info",
                    "description": "Store or process the payslip information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "amount": {"type": "string"},
                            "currency": {"type": "string"},
                            "date": {"type": "string", "description": "Date in MMDD format"}
                        },
                        "required": ["category", "amount", "currency", "date"]
                    }
                }
            }
        ]

        # Create the messages
        messages = [{"role": "user", "content": prompt}]

        # Call the API with tools
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=150,
            stream=False,
        )

        # Extract the tool call and validate it
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        logging.info(f"tool_calls: {tool_calls}")

        if tool_calls:
            if len(tool_calls) > 1:
                logging.warning(f"Found many payslips in one text: {len(tool_calls)} payslips found: {tool_calls}")
            tool_call = tool_calls[0]
            function_args = tool_call.function.arguments
            if not function_args:
                raise ValueError(f"Expected function_args in tool call but got {function_args}")

            try:
                # Parse the response using Pydantic
                payslip_info = PayslipInfo.model_validate_json(function_args)
                return payslip_info
            except ValidationError as e:
                print(f"Validation error: {e}")

        # Fallback in case of error
        return PayslipInfo(category="other", amount="0.00", currency="USD", date="0101")  # Default to January 1st

    def generate_new_filename(self, text: str, original_file_name: str) -> str:
        """
        Generate a new file name based on the payslip text.
        :param text: The text extracted from the payslip.
        :param original_file_name: The original filename of the payslip.
        :return: The new filename in the format {MM}{DD}_{category}_{amount}_{CCY}.pdf
        """
        # Extract category, amount, currency, and date using OpenAI
        payslip_info = self.get_category_amount_ccy_and_date(text)

        # Extract extension from original file name
        extension = original_file_name.split(".")[-1]

        # Format the new filename
        new_filename = f"{payslip_info.date}_{payslip_info.category}_{payslip_info.amount}_{payslip_info.currency}.{extension}"

        return new_filename

# Example usage:
# Ensure environment variables AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME are set
# openai_service = OpenAIService()
# extracted_text = "Text extracted from payslip..."
# new_filename = openai_service.generate_new_filename(extracted_text, "payslip_original.pdf")
# print(new_filename)
