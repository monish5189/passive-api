@app.get("/{tool_name}", tags=["Tools"])
async def generic_tool_page(tool_name: str):
    allowed_tools = {
        "emi",
        "gst",
        "sip",
        "qr",
        "crypto",
        "weather",
        "bmi",
        "networth",
        "roi",
        "password",
        "email",
        "forex"
    }

    if tool_name not in allowed_tools:
        raise HTTPException(
            status_code=404,
            detail="Tool not found"
        )

    return FileResponse(
        f"templates/{tool_name}.html"
    )
