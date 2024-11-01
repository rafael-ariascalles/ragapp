import os
from typing import ClassVar, Literal, Optional

import dotenv
from pydantic import BaseModel, Field

from backend.constants import ENV_FILE_PATH


class CodeGeneratorToolConfig(BaseModel):
    api_key: str | None = Field(
        default_factory=lambda: os.getenv("E2B_API_KEY"),
        description="The API key to use for the Code Generator.",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Sandbox api use api key from env variable
        # If api key is provided, also update to the environment variable
        api_key = kwargs.get("api_key")
        if api_key:
            os.environ["E2B_API_KEY"] = api_key
            dotenv.set_key(ENV_FILE_PATH, "E2B_API_KEY", api_key)


class CodeGeneratorTool(BaseModel):
    config_id: ClassVar[str] = "artifact"  # for importing
    name: Literal["CodeGenerator"] = "CodeGenerator"
    tool_type: Literal["local"] = "local"
    label: Literal["Code Generator"] = "Code Generator"
    custom_prompt: Optional[
        str
    ] = """You are a code assistant that can generate and execute code using its tools. 
Don't generate code yourself, use the provided tools instead. 
Do not show the code or sandbox url in chat, just describe the steps to build the application based on the code that is generated by your tools. 
Do not describe how to run the code, just the steps to build the application."""
    config: CodeGeneratorToolConfig | None = Field(
        default_factory=lambda: CodeGeneratorToolConfig(),
    )
    enabled: bool = False

    def validate_config(self) -> bool:
        if self.enabled and not self.config.api_key:
            raise ValueError("API key is required for enabled Code Generator tool")
        return self.config