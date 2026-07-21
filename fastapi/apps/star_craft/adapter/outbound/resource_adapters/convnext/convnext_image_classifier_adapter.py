from __future__ import annotations

import io
import logging
import os

import torch
from PIL import Image

from star_craft.app.dtos.zerg_observer_dto import LabelScore
from star_craft.app.ports.output.image_classifier_port import ImageClassifierPort

logger = logging.getLogger(__name__)

_INPUT_SIZE = 224


class ConvNextImageClassifierAdapter(ImageClassifierPort):
    """timm ConvNeXt Nano 기반 이미지 분류 어댑터.

    - backend="onnx": CPU 환경(N100) — ONNX Runtime + int8 동적 양자화
    - backend="torch": GPU 환경(Legion 4070) — torch.compile(mode="reduce-overhead")
    """

    def __init__(self, model_name: str, onnx_model_path: str, backend: str) -> None:
        self._model_name = model_name
        self._onnx_model_path = onnx_model_path
        self._backend = backend

        self._base_model = None  # timm 모델 (전처리 설정/라벨 조회/ONNX 변환에 공용으로 사용)
        self._compiled_model = None  # torch 백엔드 추론용
        self._transform = None
        self._imagenet_info = None
        self._onnx_session = None

    def classify(self, image_data: bytes, top_k: int) -> list[LabelScore]:
        tensor = self._preprocess(image_data)
        logits = self._run_onnx(tensor) if self._backend == "onnx" else self._run_torch(tensor)
        return self._to_top_k(logits, top_k)

    # ---- 전처리 / 라벨 ----

    def _get_base_model(self):
        if self._base_model is None:
            import timm

            self._base_model = timm.create_model(self._model_name, pretrained=True)
            self._base_model.eval()
        return self._base_model

    def _preprocess(self, image_data: bytes) -> torch.Tensor:
        import timm

        if self._transform is None:
            config = timm.data.resolve_data_config({}, model=self._get_base_model())
            self._transform = timm.data.create_transform(**config)

        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        return self._transform(image).unsqueeze(0)

    def _get_imagenet_info(self):
        if self._imagenet_info is None:
            from timm.data import ImageNetInfo, infer_imagenet_subset

            self._imagenet_info = ImageNetInfo(infer_imagenet_subset(self._get_base_model()))
        return self._imagenet_info

    # ---- torch 백엔드 (GPU) ----

    def _run_torch(self, tensor: torch.Tensor) -> torch.Tensor:
        if self._compiled_model is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = self._get_base_model().to(device)
            if device == "cuda":
                model = torch.compile(model, mode="reduce-overhead")
            self._compiled_model = model

        device = next(self._compiled_model.parameters()).device
        with torch.no_grad():
            return self._compiled_model(tensor.to(device))[0].cpu()

    # ---- onnx 백엔드 (CPU, int8) ----

    def _ensure_onnx_model(self) -> None:
        if os.path.exists(self._onnx_model_path):
            return

        os.makedirs(os.path.dirname(self._onnx_model_path), exist_ok=True)
        model = self._get_base_model()
        dummy = torch.zeros(1, 3, _INPUT_SIZE, _INPUT_SIZE)
        fp32_path = f"{self._onnx_model_path}.fp32.onnx"
        torch.onnx.export(
            model,
            dummy,
            fp32_path,
            input_names=["input"],
            output_names=["logits"],
            dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
            opset_version=17,
        )

        from onnxruntime.quantization import QuantType, quantize_dynamic

        quantize_dynamic(fp32_path, self._onnx_model_path, weight_type=QuantType.QInt8)
        os.remove(fp32_path)
        logger.info(
            "[ConvNextImageClassifierAdapter] ONNX int8 양자화 모델 생성 완료 → %s",
            self._onnx_model_path,
        )

    def _get_onnx_session(self):
        if self._onnx_session is None:
            self._ensure_onnx_model()
            import onnxruntime as ort

            self._onnx_session = ort.InferenceSession(
                self._onnx_model_path, providers=["CPUExecutionProvider"]
            )
        return self._onnx_session

    def _run_onnx(self, tensor: torch.Tensor) -> torch.Tensor:
        session = self._get_onnx_session()
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: tensor.numpy()})
        return torch.from_numpy(outputs[0])[0]

    # ---- 공통 ----

    def _to_top_k(self, logits: torch.Tensor, top_k: int) -> list[LabelScore]:
        probs = torch.softmax(logits, dim=-1)
        values, indices = torch.topk(probs, k=top_k)
        info = self._get_imagenet_info()
        return [
            LabelScore(label=info.index_to_description(int(idx)), confidence=float(val))
            for val, idx in zip(values.tolist(), indices.tolist())
        ]
