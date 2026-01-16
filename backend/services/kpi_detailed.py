"""
Detailed KPI Parameter Breakdown Service.
Computes parameter-level breakdown using the ACTUAL KPI calculation logic from kpi.py.
NO dummy data - everything comes from real backend computation.
"""

from typing import Dict, List, Any, Optional
from config.database import get_db, close_db, Batch, Block
from services.kpi import KPIService
from utils.parse_numeric import parse_numeric
import math
import logging

logger = logging.getLogger(__name__)


def get_kpi_detailed_breakdown(batch_id: str, kpi_type: str) -> Dict[str, Any]:
    """
    Get detailed parameter breakdown for a specific KPI type.
    Uses the ACTUAL KPI calculation logic from kpi.py.
    
    Args:
        batch_id: Batch ID
        kpi_type: One of 'fsr', 'infrastructure', 'placement', 'lab', 'overall'
    
    Returns:
        Dict with parameter breakdown, evidence, calculation steps
    """
    db = get_db()
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")
        
        # Get all blocks and aggregate data
        blocks = db.query(Block).filter(Block.batch_id == batch_id).all()
        aggregated_data = {}
        evidence_map = {}  # Map parameter names to evidence snippets
        
        for block in blocks:
            if block.data and isinstance(block.data, dict):
                aggregated_data.update(block.data)
                # Store evidence for parameters found in this block
                for key, value in block.data.items():
                    if value is not None and value != "":
                        if key not in evidence_map:
                            evidence_map[key] = {
                                "snippet": block.evidence_snippet or "",
                                "page": block.evidence_page or 1,
                                "source_doc": block.source_doc or ""
                            }
        
        mode = batch.mode or "aicte"
        kpi_service = KPIService()
        
        # PRODUCTION HARDENING: Use official KPI service for all modes
        from services.kpi_official import OfficialKPIService
        from services.evidence_tracker import EvidenceTracker
        
        official_service = OfficialKPIService()
        
        # Build proper evidence map from blocks
        block_dicts = [{
            "data": block.data or {},
            "evidence_snippet": block.evidence_snippet,
            "evidence_page": block.evidence_page,
            "source_doc": block.source_doc
        } for block in blocks]
        evidence_map = EvidenceTracker.build_evidence_map(block_dicts)
        
        # Compute detailed breakdown based on KPI type and mode
        if mode.lower() == "aicte":
            if kpi_type == "fsr":
                return _compute_fsr_detailed(aggregated_data, mode, evidence_map)
            elif kpi_type == "infrastructure":
                return _compute_infrastructure_detailed(aggregated_data, mode, evidence_map)
            elif kpi_type == "placement":
                return _compute_placement_detailed(aggregated_data, mode, evidence_map)
            elif kpi_type == "lab":
                return _compute_lab_detailed(aggregated_data, mode, evidence_map)
            elif kpi_type == "overall":
                return _compute_overall_detailed(batch_id, aggregated_data, mode, evidence_map, blocks)
        elif mode.lower() == "nba":
            # NBA mode - use official service
            if kpi_type == "peos_psos":
                score, info = official_service.calculate_nba_peos_psos(aggregated_data, evidence_map)
            elif kpi_type == "faculty_quality":
                score, info = official_service.calculate_nba_faculty_quality(aggregated_data, evidence_map)
            elif kpi_type == "student_performance":
                score, info = official_service.calculate_nba_student_performance(aggregated_data, evidence_map)
            elif kpi_type == "continuous_improvement":
                score, info = official_service.calculate_nba_continuous_improvement(aggregated_data, evidence_map)
            elif kpi_type == "co_po_mapping":
                score, info = official_service.calculate_nba_co_po_mapping(aggregated_data, evidence_map)
            elif kpi_type == "overall":
                return _compute_overall_detailed(batch_id, aggregated_data, mode, evidence_map, blocks)
            else:
                raise ValueError(f"Invalid NBA KPI type: {kpi_type}")
            
            if kpi_type != "overall":
                return _format_kpi_details(kpi_type, score, info, evidence_map)
        elif mode.lower() == "naac":
            # NAAC mode - use official service
            if kpi_type.startswith("criterion_"):
                score, info = official_service.calculate_naac_criterion(kpi_type, aggregated_data, evidence_map)
                return _format_kpi_details(kpi_type, score, info, evidence_map)
            elif kpi_type == "overall":
                return _compute_overall_detailed(batch_id, aggregated_data, mode, evidence_map, blocks)
        elif mode.lower() == "nirf":
            # NIRF mode - use official service
            if kpi_type in ["tlr", "rp", "go", "oi", "pr"]:
                score, info = official_service.calculate_nirf_parameter(kpi_type, aggregated_data, evidence_map)
                return _format_kpi_details(kpi_type, score, info, evidence_map)
            elif kpi_type == "overall":
                return _compute_overall_detailed(batch_id, aggregated_data, mode, evidence_map, blocks)
        
        raise ValueError(f"Invalid KPI type '{kpi_type}' for mode '{mode}'")
    
    finally:
        close_db(db)


def _format_kpi_details(kpi_type: str, score: Optional[float], info: Dict[str, Any], evidence_map: Dict[str, Any]) -> Dict[str, Any]:
    """Format KPI details response from official service output."""
    parameters = []
    formula_steps = []
    
    # Extract parameters from info
    if "components" in info:
        for comp_name, comp_score in info["components"].items():
            evidence = info.get("evidence", {}).get(comp_name, {})
            parameters.append({
                "parameter_name": comp_name,
                "raw_value": evidence.get("value"),
                "normalized_value": comp_score,
                "score": comp_score,
                "contribution": info.get("weights", {}).get(comp_name, 0),
                "evidence": {
                    "snippet": evidence.get("snippet", ""),
                    "page": evidence.get("page", 1),
                    "source_doc": evidence.get("source_doc", "")
                }
            })
    
    # Formula steps
    if "formula" in info:
        formula_steps.append({
            "step": 1,
            "description": info["formula"],
            "result": score
        })
    
    return {
        "kpi_type": kpi_type,
        "score": score,
        "formula_text": info.get("formula", ""),
        "parameters": parameters,
        "formula_steps": formula_steps,
        "missing_parameters": info.get("excluded", []),
        "data_quality": "complete" if score is not None else "incomplete",
        "confidence": 1.0 if score is not None else 0.0,
        "evidence": info.get("evidence", {})
    }


def _compute_fsr_detailed(data: Dict, mode: str, evidence_map: Dict) -> Dict[str, Any]:
    """Compute FSR detailed breakdown using actual calculation logic."""
    parameters = []
    calculation_steps = []
    
    # Extract parameters (same logic as kpi.py)
    faculty_count = (
        data.get("faculty_count_num") or
        parse_numeric(data.get("faculty_count")) or 
        parse_numeric(data.get("faculty")) or 
        parse_numeric(data.get("total_faculty"))
    )
    
    student_count = (
        data.get("student_count_num") or
        data.get("total_intake_num") or
        parse_numeric(data.get("total_students")) or
        parse_numeric(data.get("student_count")) or 
        parse_numeric(data.get("students")) or
        parse_numeric(data.get("total_intake")) or
        parse_numeric(data.get("admitted_students"))
    )
    
    # Try programs_approved fallback
    if student_count is None:
        programs = data.get("programs_approved", [])
        if isinstance(programs, list):
            total_intake = 0
            for program in programs:
                if isinstance(program, dict):
                    intake = parse_numeric(program.get("intake_2025_26") or program.get("intake") or program.get("students"))
                    if intake:
                        total_intake += intake
            if total_intake > 0:
                student_count = total_intake
    
    # Parameter: Faculty Count
    faculty_evidence = _find_evidence("faculty_count", evidence_map, data)
    parameters.append({
        "name": "faculty_count",
        "display_name": "Total Faculty",
        "extracted": faculty_count,
        "norm": "As per intake",
        "weight": 1.0,
        "contrib": 0.0,  # FSR doesn't use weighted contribution
        "unit": "persons",
        "missing": faculty_count is None,
        "evidence": faculty_evidence
    })
    
    # Parameter: Student Count
    student_evidence = _find_evidence("total_students", evidence_map, data)
    parameters.append({
        "name": "total_students",
        "display_name": "Total Students",
        "extracted": student_count,
        "norm": "As per sanctioned intake",
        "weight": 1.0,
        "contrib": 0.0,
        "unit": "persons",
        "missing": student_count is None,
        "evidence": student_evidence
    })
    
    # Calculate FSR score - OFFICIAL FORMULA
    # FSR = Total Students / Total Faculty (NOT Faculty/Students)
    final_score = None
    if faculty_count is not None and student_count is not None:
        if student_count == 0 or faculty_count == 0:
            final_score = None
        else:
            # OFFICIAL FORMULA: FSR = Students / Faculty
            fsr = student_count / faculty_count
            
            calculation_steps.append({
                "step": 1,
                "description": "Calculate Faculty-Student Ratio",
                "formula": f"FSR = student_count / faculty_count = {student_count} / {faculty_count}",
                "result": round(fsr, 4)
            })
            
            # Official scoring rule
            if fsr <= 15:
                final_score = 100.0
                calculation_steps.append({
                    "step": 2,
                    "description": "Compare with AICTE norm (FSR ≤ 15)",
                    "formula": "FSR ≤ 15 → Score = 100",
                    "result": 100.0
                })
            elif fsr <= 20:
                # Linear scale: 100 at FSR=15, 60 at FSR=20
                score = 100 + (fsr - 15) * (-8)
                final_score = round(score, 2)
                calculation_steps.append({
                    "step": 2,
                    "description": "Linear scale (15 < FSR ≤ 20)",
                    "formula": f"Score = 100 + (FSR - 15) × (-8) = 100 + ({fsr} - 15) × (-8)",
                    "result": final_score
                })
            else:
                # Proportional penalty: FSR > 20
                penalty = (fsr - 20) * 3
                score = max(0.0, 60.0 - penalty)
                final_score = round(score, 2)
                calculation_steps.append({
                    "step": 2,
                    "description": "Proportional penalty (FSR > 20)",
                    "formula": f"Score = 60 - (FSR - 20) × 3 = 60 - ({fsr} - 20) × 3",
                    "result": final_score
                })
    
    return {
        "kpi_type": "fsr",
        "kpi_name": "Faculty-Student Ratio Score",
        "score": round(final_score, 2) if final_score is not None else None,
        "weightages": {
            "faculty_count": 1.0,
            "total_students": 1.0
        },
        "parameters": parameters,
        "calculation_steps": calculation_steps,
        "formula": "FSR = Students / Faculty; FSR ≤ 15 → 100, 15 < FSR ≤ 20 → linear (100→60), FSR > 20 → penalty",
        "evidence": {}
    }


def _compute_infrastructure_detailed(data: Dict, mode: str, evidence_map: Dict) -> Dict[str, Any]:
    """Compute Infrastructure detailed breakdown using actual calculation logic."""
    parameters = []
    calculation_steps = []
    
    # Get student count (required for norms)
    student_count = (
        data.get("total_students_num")
        or data.get("student_count_num")
        or data.get("total_intake_num")
        or parse_numeric(data.get("total_students"))
        or parse_numeric(data.get("student_count"))
        or parse_numeric(data.get("total_intake"))
        or parse_numeric(data.get("admitted_students"))
    )
    
    if student_count is None or student_count == 0:
        return {
            "kpi_type": "infrastructure",
            "kpi_name": "Infrastructure Score",
            "score": None,
            "weightages": {},
            "parameters": [],
            "calculation_steps": [{"step": 1, "description": "Student count missing - cannot calculate infrastructure score", "formula": "N/A", "result": None}],
            "formula": "Weighted sum: Area(40%) + Classrooms(25%) + Library(15%) + Digital(10%) + Hostel(10%)",
            "evidence": {}
        }
    
    # 1. Area Score (40% weight)
    built_up_area_sqm = (
        data.get("built_up_area_sqm_num")
        or data.get("built_up_area_num")
    )
    
    if built_up_area_sqm is None:
        raw_area = (
            data.get("built_up_area_raw")
            or data.get("built_up_area")
            or data.get("area")
            or data.get("total_area")
        )
        if raw_area:
            from utils.parse_numeric_with_metadata import parse_numeric_with_metadata
            meta = parse_numeric_with_metadata(raw_area)
            built_up_area_sqm = meta.get("sqm") or meta.get("value")
    
    required_area = student_count * 4  # AICTE norm: 4 sqm per student
    area_score = 0.0
    area_contrib = 0.0
    
    if built_up_area_sqm is None:
        area_score = 0.0
    else:
        area_score = min(100.0, (built_up_area_sqm / required_area) * 100) if required_area > 0 else 0.0
        area_score_normalized = area_score / 100.0
        area_contrib = 0.40 * area_score_normalized * 100
    
    area_evidence = _find_evidence("built_up_area", evidence_map, data)
    parameters.append({
        "name": "built_up_area",
        "display_name": "Built-up Area",
        "extracted": built_up_area_sqm,
        "norm": required_area,
        "weight": 0.40,
        "contrib": round(area_contrib, 2),
        "unit": "sqm",
        "missing": built_up_area_sqm is None,
        "evidence": area_evidence
    })
    
    # 2. Classroom Score (25% weight)
    actual_classrooms = (
        parse_numeric(data.get("total_classrooms"))
        or parse_numeric(data.get("classrooms"))
        or parse_numeric(data.get("number_of_classrooms"))
        or 0
    )
    required_classrooms = math.ceil(student_count / 40)  # AICTE norm: 40 students per classroom
    classroom_score = min(1.0, actual_classrooms / required_classrooms) if required_classrooms > 0 else 0.0
    classroom_contrib = 0.25 * classroom_score * 100
    
    classroom_evidence = _find_evidence("classrooms", evidence_map, data)
    parameters.append({
        "name": "classrooms",
        "display_name": "Classrooms",
        "extracted": actual_classrooms,
        "norm": required_classrooms,
        "weight": 0.25,
        "contrib": round(classroom_contrib, 2),
        "unit": "count",
        "missing": actual_classrooms == 0,
        "evidence": classroom_evidence
    })
    
    # 3. Library Score (15% weight)
    library_area_sqm = (
        parse_numeric(data.get("library_area_sqm"))
        or parse_numeric(data.get("library_area"))
        or 0
    )
    required_library = student_count * 0.5  # 0.5 sqm per student
    library_score = min(1.0, library_area_sqm / required_library) if required_library > 0 else 0.0
    library_contrib = 0.15 * library_score * 100
    
    library_evidence = _find_evidence("library_area", evidence_map, data)
    parameters.append({
        "name": "library_area",
        "display_name": "Library Area",
        "extracted": library_area_sqm,
        "norm": required_library,
        "weight": 0.15,
        "contrib": round(library_contrib, 2),
        "unit": "sqm",
        "missing": library_area_sqm == 0,
        "evidence": library_evidence
    })
    
    # 4. Digital Resources Score (10% weight)
    digital_resources = (
        parse_numeric(data.get("digital_library_resources"))
        or parse_numeric(data.get("digital_resources"))
        or 0
    )
    digital_score = min(1.0, digital_resources / 500)  # 500 resources = 100%
    digital_contrib = 0.10 * digital_score * 100
    
    digital_evidence = _find_evidence("digital_resources", evidence_map, data)
    parameters.append({
        "name": "digital_resources",
        "display_name": "Digital Resources",
        "extracted": digital_resources,
        "norm": 500,
        "weight": 0.10,
        "contrib": round(digital_contrib, 2),
        "unit": "count",
        "missing": digital_resources == 0,
        "evidence": digital_evidence
    })
    
    # 5. Hostel Score (10% weight)
    hostel_capacity = (
        parse_numeric(data.get("hostel_capacity"))
        or 0
    )
    required_hostel = student_count * 0.4  # 40% of students need hostel
    hostel_score = min(1.0, hostel_capacity / required_hostel) if required_hostel > 0 else 0.0
    hostel_contrib = 0.10 * hostel_score * 100
    
    hostel_evidence = _find_evidence("hostel_capacity", evidence_map, data)
    parameters.append({
        "name": "hostel_capacity",
        "display_name": "Hostel Capacity",
        "extracted": hostel_capacity,
        "norm": required_hostel,
        "weight": 0.10,
        "contrib": round(hostel_contrib, 2),
        "unit": "persons",
        "missing": hostel_capacity == 0,
        "evidence": hostel_evidence
    })
    
    # Final score
    final_score = 100 * (
        0.40 * (area_score / 100.0) +
        0.25 * classroom_score +
        0.15 * library_score +
        0.10 * digital_score +
        0.10 * hostel_score
    )
    
    # Add calculation steps
    step_num = 1
    for param in parameters:
        if not param["missing"]:
            calculation_steps.append({
                "step": step_num,
                "description": f"Calculate {param['display_name']} contribution",
                "formula": f"score = min(100, (extracted / norm) × 100) × weight = min(100, ({param['extracted']} / {param['norm']}) × 100) × {param['weight']*100}%",
                "result": param["contrib"]
            })
            step_num += 1
    
    calculation_steps.append({
        "step": step_num,
        "description": "Sum all contributions",
        "formula": "infrastructure_score = Σ(contributions)",
        "result": round(final_score, 2)
    })
    
    return {
        "kpi_type": "infrastructure",
        "kpi_name": "Infrastructure Score",
        "score": round(final_score, 2),
        "weightages": {
            "built_up_area": 0.40,
            "classrooms": 0.25,
            "library_area": 0.15,
            "digital_resources": 0.10,
            "hostel_capacity": 0.10
        },
        "parameters": parameters,
        "calculation_steps": calculation_steps,
        "formula": "infrastructure_score = (Area×0.40) + (Classrooms×0.25) + (Library×0.15) + (Digital×0.10) + (Hostel×0.10)",
        "evidence": {}
    }


def _compute_placement_detailed(data: Dict, mode: str, evidence_map: Dict) -> Dict[str, Any]:
    """Compute Placement Index detailed breakdown using actual calculation logic."""
    parameters = []
    calculation_steps = []
    
    # Extract placement rate (same logic as kpi.py)
    placement_rate = (
        data.get("placement_rate_num")
        or parse_numeric(data.get("placement_percentage"))
        or parse_numeric(data.get("placement_rate"))
    )
    
    students_placed = None
    students_eligible = None
    
    if placement_rate is None:
        students_placed = (
            data.get("students_placed_num") or
            data.get("total_placements_num") or
            parse_numeric(data.get("students_placed")) or
            parse_numeric(data.get("total_placements")) or
            parse_numeric(data.get("placement_count"))
        )
        
        students_eligible = (
            data.get("students_eligible_num") or
            data.get("student_count_num") or
            data.get("total_intake_num") or
            parse_numeric(data.get("students_eligible")) or
            parse_numeric(data.get("total_students")) or
            parse_numeric(data.get("student_count")) or
            parse_numeric(data.get("total_intake")) or
            parse_numeric(data.get("admitted_students"))
        )
        
        if students_placed is not None and students_eligible is not None and students_eligible > 0:
            placement_rate = (students_placed / students_eligible) * 100
    
    # Parameter: Placement Rate
    placement_evidence = _find_evidence("placement_rate", evidence_map, data)
    parameters.append({
        "name": "placement_rate",
        "display_name": "Placement Rate",
        "extracted": placement_rate,
        "norm": 100.0,  # 100% is ideal
        "weight": 1.0,
        "contrib": min(placement_rate, 100.0) if placement_rate else 0.0,
        "unit": "%",
        "missing": placement_rate is None,
        "evidence": placement_evidence
    })
    
    # Calculate final score
    final_score = min(placement_rate, 100.0) if placement_rate else None
    
    if placement_rate is not None:
        calculation_steps.append({
            "step": 1,
            "description": "Calculate Placement Rate",
            "formula": f"placement_rate = {placement_rate}%",
            "result": round(placement_rate, 2)
        })
        calculation_steps.append({
            "step": 2,
            "description": "Cap at 100%",
            "formula": "placement_index = min(placement_rate, 100)",
            "result": round(final_score, 2)
        })
    
    return {
        "kpi_type": "placement",
        "kpi_name": "Placement Index",
        "score": round(final_score, 2) if final_score is not None else None,
        "weightages": {
            "placement_rate": 1.0
        },
        "parameters": parameters,
        "calculation_steps": calculation_steps,
        "formula": "placement_index = min(placement_rate, 100)",
        "evidence": {}
    }


def _compute_lab_detailed(data: Dict, mode: str, evidence_map: Dict) -> Dict[str, Any]:
    """Compute Lab Compliance detailed breakdown using actual calculation logic."""
    parameters = []
    calculation_steps = []
    
    # Extract available labs (same logic as kpi.py)
    available_labs = (
        data.get("total_labs_num") or
        data.get("lab_count_num") or
        data.get("total_labs") or
        parse_numeric(data.get("total_labs")) or
        parse_numeric(data.get("lab_count")) or 
        parse_numeric(data.get("labs")) or 
        parse_numeric(data.get("laboratories"))
    )
    
    # Calculate required labs
    required_labs = (
        data.get("required_labs_num") or
        parse_numeric(data.get("required_labs"))
    )
    
    if required_labs is None:
        student_count = (
            data.get("student_count_num") or
            data.get("total_intake_num") or
            parse_numeric(data.get("total_students")) or
            parse_numeric(data.get("student_count")) or
            parse_numeric(data.get("total_intake")) or
            parse_numeric(data.get("admitted_students"))
        )
        if student_count and student_count > 0:
            required_labs = max(5, student_count // 50)  # At least 1 lab per 50 students, minimum 5
        else:
            required_labs = 5  # Default minimum
    
    # Parameter: Available Labs
    lab_evidence = _find_evidence("total_labs", evidence_map, data)
    parameters.append({
        "name": "available_labs",
        "display_name": "Available Labs",
        "extracted": available_labs,
        "norm": required_labs,
        "weight": 1.0,
        "contrib": 0.0,  # Lab compliance doesn't use weighted contribution
        "unit": "count",
        "missing": available_labs is None,
        "evidence": lab_evidence
    })
    
    # Calculate final score
    final_score = None
    if available_labs is not None and required_labs > 0:
        lab_compliance = (available_labs / required_labs) * 100
        final_score = min(lab_compliance, 100.0)
        
        calculation_steps.append({
            "step": 1,
            "description": "Calculate Lab Compliance",
            "formula": f"compliance = (available_labs / required_labs) × 100 = ({available_labs} / {required_labs}) × 100",
            "result": round(lab_compliance, 2)
        })
        calculation_steps.append({
            "step": 2,
            "description": "Cap at 100%",
            "formula": "lab_compliance_index = min(compliance, 100)",
            "result": round(final_score, 2)
        })
    
    return {
        "kpi_type": "lab",
        "kpi_name": "Lab Compliance Index",
        "score": round(final_score, 2) if final_score is not None else None,
        "weightages": {
            "available_labs": 1.0
        },
        "parameters": parameters,
        "calculation_steps": calculation_steps,
        "formula": "lab_compliance_index = min((available_labs / required_labs) × 100, 100)",
        "evidence": {}
    }


def _compute_overall_detailed(batch_id: str, data: Dict, mode: str, evidence_map: Dict, blocks: List) -> Dict[str, Any]:
    """Compute Overall Score detailed breakdown."""
    parameters = []
    calculation_steps = []
    
    # Get KPI results from batch
    db = get_db()
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        kpi_results = batch.kpi_results or {}
        
        # Helper function to extract value from either dict or direct numeric
        def extract_kpi_value(key):
            val = kpi_results.get(key)
            if val is None:
                return None
            if isinstance(val, dict):
                return val.get("value")
            # Direct numeric value (from system batches)
            if isinstance(val, (int, float)):
                return val
            return None
        
        # Extract individual KPI scores (handles both formats)
        fsr = extract_kpi_value("fsr_score")
        infra = extract_kpi_value("infrastructure_score")
        placement = extract_kpi_value("placement_index")
        lab = extract_kpi_value("lab_compliance_index")
        
        # AICTE Overall calculation (same logic as kpi.py)
        if mode.lower() == "aicte":
            # If FSR is available: average FSR + Placement + Lab (ignore infra)
            # If FSR is missing: average Infrastructure + Placement + Lab
            if fsr is not None:
                kpi_values = [v for v in [fsr, placement, lab] if v is not None]
                included_kpis = []
                if fsr is not None:
                    included_kpis.append("FSR")
                if placement is not None:
                    included_kpis.append("Placement")
                if lab is not None:
                    included_kpis.append("Lab")
                excluded = "Infrastructure (excluded when FSR is available)"
            else:
                kpi_values = [v for v in [infra, placement, lab] if v is not None]
                included_kpis = []
                if infra is not None:
                    included_kpis.append("Infrastructure")
                if placement is not None:
                    included_kpis.append("Placement")
                if lab is not None:
                    included_kpis.append("Lab")
                excluded = "FSR (missing, using Infrastructure instead)"
            
            if kpi_values:
                overall_score = sum(kpi_values) / len(kpi_values)
                
                # Add parameters
                if fsr is not None:
                    parameters.append({
                        "name": "fsr_score",
                        "display_name": "FSR Score",
                        "extracted": fsr,
                        "norm": 100.0,
                        "weight": 1.0 / len(kpi_values),
                        "contrib": fsr / len(kpi_values),
                        "unit": "score",
                        "missing": False,
                        "evidence": {}
                    })
                
                if infra is not None and fsr is None:
                    parameters.append({
                        "name": "infrastructure_score",
                        "display_name": "Infrastructure Score",
                        "extracted": infra,
                        "norm": 100.0,
                        "weight": 1.0 / len(kpi_values),
                        "contrib": infra / len(kpi_values),
                        "unit": "score",
                        "missing": False,
                        "evidence": {}
                    })
                
                if placement is not None:
                    parameters.append({
                        "name": "placement_index",
                        "display_name": "Placement Index",
                        "extracted": placement,
                        "norm": 100.0,
                        "weight": 1.0 / len(kpi_values),
                        "contrib": placement / len(kpi_values),
                        "unit": "score",
                        "missing": False,
                        "evidence": {}
                    })
                
                if lab is not None:
                    parameters.append({
                        "name": "lab_compliance_index",
                        "display_name": "Lab Compliance Index",
                        "extracted": lab,
                        "norm": 100.0,
                        "weight": 1.0 / len(kpi_values),
                        "contrib": lab / len(kpi_values),
                        "unit": "score",
                        "missing": False,
                        "evidence": {}
                    })
                
                calculation_steps.append({
                    "step": 1,
                    "description": f"Included KPIs: {', '.join(included_kpis)}",
                    "formula": f"Excluded: {excluded}",
                    "result": f"{len(kpi_values)} KPIs"
                })
                
                calculation_steps.append({
                    "step": 2,
                    "description": "Calculate average",
                    "formula": f"overall = ({' + '.join(str(v) for v in kpi_values)}) / {len(kpi_values)}",
                    "result": round(overall_score, 2)
                })
                
                return {
                    "kpi_type": "overall",
                    "kpi_name": "AICTE Overall Score",
                    "score": round(overall_score, 2),
                    "weightages": {kpi: 1.0 / len(kpi_values) for kpi in included_kpis},
                    "parameters": parameters,
                    "calculation_steps": calculation_steps,
                    "formula": f"overall = average({', '.join(included_kpis)})",
                    "evidence": {},
                    "included_kpis": included_kpis,
                    "excluded_kpis": [excluded]
                }
            else:
                return {
                    "kpi_type": "overall",
                    "kpi_name": "AICTE Overall Score",
                    "score": None,
                    "weightages": {},
                    "parameters": [],
                    "calculation_steps": [{"step": 1, "description": "Insufficient KPI data", "formula": "N/A", "result": None}],
                    "formula": "overall = average(available KPIs)",
                    "evidence": {}
                }
        else:
            # UGC Overall (if needed)
            return {
                "kpi_type": "overall",
                "kpi_name": "Overall Score",
                "score": None,
                "weightages": {},
                "parameters": [],
                "calculation_steps": [],
                "formula": "N/A",
                "evidence": {}
            }
    finally:
        close_db(db)


def _find_evidence(param_name: str, evidence_map: Dict, data: Dict) -> Dict[str, Any]:
    """Find evidence snippet for a parameter."""
    # Try direct match
    if param_name in evidence_map:
        return {
            "snippet": evidence_map[param_name].get("snippet", ""),
            "page": evidence_map[param_name].get("page", 1),
            "source_doc": evidence_map[param_name].get("source_doc", "")
        }
    
    # Try aliases
    aliases = {
        "faculty_count": ["faculty", "total_faculty", "teaching_staff"],
        "total_students": ["student_count", "students", "total_intake", "admitted_students"],
        "built_up_area": ["area", "total_area", "building_area"],
        "classrooms": ["classroom_count", "number_of_classrooms", "total_classrooms"],
        "library_area": ["library_size", "library_space"],
        "digital_resources": ["digital_library_resources"],
        "hostel_capacity": ["hostel"],
        "placement_rate": ["placement_percentage", "placement_ratio"],
        "total_labs": ["lab_count", "labs", "laboratories", "total_labs_num"]
    }
    
    for alias in aliases.get(param_name, []):
        if alias in evidence_map:
            return {
                "snippet": evidence_map[alias].get("snippet", ""),
                "page": evidence_map[alias].get("page", 1),
                "source_doc": evidence_map[alias].get("source_doc", "")
            }
    
    return {
        "snippet": "",
        "page": 1,
        "source_doc": ""
    }

