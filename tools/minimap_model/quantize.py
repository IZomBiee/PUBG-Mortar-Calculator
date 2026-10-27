from pathlib import Path
import onnx
import torch
from tools.minimap_model.model import MinimapModel
from onnxruntime.quantization import (
    QuantType,
    quantize_dynamic,
)

from tools.minimap_model import shared


model = MinimapModel(num_classes=3, pretrained=False)
model.load_state_dict(
    torch.load(Path("tools/minimap_model/best.pth"), map_location="cpu")
)
model.eval()

fp32_onnx_path = Path("tools/minimap_model/best_fp32.onnx")
int8_onnx_path = Path("tools/minimap_model/best_int8.onnx")
dummy_input = torch.randn(1, 3, shared.RESOLUTION, shared.RESOLUTION)

torch.onnx.export(
    model,
    dummy_input,
    str(fp32_onnx_path),
    export_params=True,
    opset_version=14,
    do_constant_folding=True,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
)

onnx_model = onnx.load(str(fp32_onnx_path))
meta = onnx_model.metadata_props.add()
meta.key = "cut_factor"
meta.value = str(shared.CUT_FACTOR)

onnx_model.graph.ClearField("value_info")
onnx.save(onnx_model, str(fp32_onnx_path), save_as_external_data=False)

quantize_dynamic(
    model_input=str(fp32_onnx_path),
    model_output=str(int8_onnx_path),
    op_types_to_quantize=["Conv", "MatMul", "Gemm"],
    weight_type=QuantType.QInt8,
    extra_options={"save_as_external_data": False},
)

final_model = onnx.load(str(int8_onnx_path))

meta = final_model.metadata_props.add()
meta.key = "cut_factor"
meta.value = str(shared.CUT_FACTOR)

onnx.save(final_model, str(int8_onnx_path), save_as_external_data=False)

external_data_file = Path(f"{int8_onnx_path}.data")
if external_data_file.exists():
    external_data_file.unlink()

print(f"Quantized model generated: {int8_onnx_path.stat().st_size / (1024 * 1024):.2f} MB")