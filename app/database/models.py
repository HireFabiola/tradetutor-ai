from pydantic import BaseModel,  Field, model_validator

class ScenarioAnswer(BaseModel):
    numeric_answer: float = Field(gt=0, description="The numeric answer for the scenario")
    reasoning_text: str = Field(min_length=15, max_length=200, description="The reasoning behind the answer")
    entry_price: float = Field(gt=0, description="The trade entry price")
    stop_loss_price: float = Field(gt=0, description="The stop-loss price")

    @model_validator(mode="after")
    def stop_loss_must_differ_from_entry(self):
        if self.entry_price == self.stop_loss_price:
            raise ValueError("Stop-loss price cannot equal entry price — risk would be zero.")
        return self
