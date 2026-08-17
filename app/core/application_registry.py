"""
Application Runtime Registry

Maps application IDs to executable entry points.
"""

from applications.loan_ml.app import run as loan_ml
from applications.loan_dl.app import run as loan_dl
from applications.loan_xai.app import run as loan_xai
from applications.loan_rag.app import run as loan_rag
from applications.loan_agent.app import run_app as loan_agent
from applications.loan_multi_agent.app import run as loan_multi_agent

from applications.hr_ml.app import run as hr_ml
from applications.hr_dl.app import run as hr_dl
from applications.hr_xai.app import run as hr_xai
from applications.hr_rag.app import run as hr_rag
from applications.hr_agent.app import run_app as hr_agent
from applications.hr_multi_agent.app import run as hr_multi_agent

from applications.rag_projects.uc1.app import run as rag_uc1
from applications.rag_projects.uc2.app import run as rag_uc2
from applications.rag_projects.uc3.app import run as rag_uc3
from applications.rag_projects.uc4.app import run as rag_uc4
from applications.rag_projects.uc5.app import run as rag_uc5
from applications.rag_projects.uc6.app import run as rag_uc6
from applications.rag_projects.uc7.app import run as rag_uc7

from applications.agent_projects.uc1.app import run as agent_uc1
from applications.agent_projects.uc2.app import run as agent_uc2
from applications.agent_projects.uc3.app import run as agent_uc3
from applications.agent_projects.uc4.app import run as agent_uc4

from applications.mas_projects.uc1.app import run as mas_uc1
from applications.mas_projects.uc2.app import run as mas_uc2
from applications.mas_projects.uc3.app import run as mas_uc3
from applications.mas_projects.uc4.app import run as mas_uc4

from applications.media_projects.uc1.app import run as media_uc1
from applications.media_projects.uc2.app import run as media_uc2
from applications.media_projects.uc3.app import run as media_uc3
from applications.media_projects.uc4.app import run as media_uc4

from applications.prompt_projects.uc1.app import run as prompt_uc1
from applications.prompt_projects.uc2.app import run as prompt_uc2
from applications.prompt_projects.uc3.app import run as prompt_uc3
from applications.prompt_projects.uc4.app import run as prompt_uc4

from applications.aiopt_projects.uc1.app import run as aiopt_uc1
from applications.aiopt_projects.uc2.app import run as aiopt_uc2
from applications.aiopt_projects.uc3.app import run as aiopt_uc3
from applications.aiopt_projects.uc4.app import run as aiopt_uc4

from applications.llm_evaluation.uc1.app import run as llmeval_uc1
from applications.llm_evaluation.uc2.app import run as llmeval_uc2
from applications.llm_evaluation.uc3.app import run as llmeval_uc3
from applications.llm_evaluation.uc4.app import run as llmeval_uc4

from applications.finetune_projects.uc1.app import run as finetune_uc1
from applications.finetune_projects.uc2.app import run as finetune_uc2
from applications.finetune_projects.uc3.app import run as finetune_uc3
from applications.finetune_projects.uc4.app import run as finetune_uc4

from applications.sysdesign_projects.uc1.app import run as sysdesign_uc1
from applications.sysdesign_projects.uc2.app import run as sysdesign_uc2
from applications.sysdesign_projects.uc3.app import run as sysdesign_uc3
from applications.sysdesign_projects.uc4.app import run as sysdesign_uc4

APPLICATION_RUNNERS = {
    "loan_ml": loan_ml,
    "loan_dl": loan_dl,
    "loan_xai": loan_xai,
    "loan_rag": loan_rag,
    "loan_agent": loan_agent,
    "loan_multi_agent": loan_multi_agent,
    "hr_ml": hr_ml,
    "hr_dl": hr_dl,
    "hr_xai": hr_xai,
    "hr_rag": hr_rag,
    "hr_agent": hr_agent,
    "hr_multi_agent": hr_multi_agent,
    "rag_uc1": rag_uc1,
    "rag_uc2": rag_uc2,
    "rag_uc3": rag_uc3,
    "rag_uc4": rag_uc4,
    "rag_uc5": rag_uc5,
    "rag_uc6": rag_uc6,
    "rag_uc7": rag_uc7,
    "agent_uc1": agent_uc1,
    "agent_uc2": agent_uc2,
    "agent_uc3": agent_uc3,
    "agent_uc4": agent_uc4,
    "mas_uc1": mas_uc1,
    "mas_uc2": mas_uc2,
    "mas_uc3": mas_uc3,
    "mas_uc4": mas_uc4,
    "media_uc1": media_uc1,
    "media_uc2": media_uc2,
    "media_uc3": media_uc3,
    "media_uc4": media_uc4,
    "prompt_uc1": prompt_uc1,
    "prompt_uc2": prompt_uc2,
    "prompt_uc3": prompt_uc3,
    "prompt_uc4": prompt_uc4,
    "aiopt_uc1": aiopt_uc1,
    "aiopt_uc2": aiopt_uc2,
    "aiopt_uc3": aiopt_uc3,
    "aiopt_uc4": aiopt_uc4,
    "llmeval_uc1": llmeval_uc1,
    "llmeval_uc2": llmeval_uc2,
    "llmeval_uc3": llmeval_uc3,
    "llmeval_uc4": llmeval_uc4,
    "finetune_uc1": finetune_uc1,
    "finetune_uc2": finetune_uc2,
    "finetune_uc3": finetune_uc3,
    "finetune_uc4": finetune_uc4,
    "sysdesign_uc1": sysdesign_uc1,
    "sysdesign_uc2": sysdesign_uc2,
    "sysdesign_uc3": sysdesign_uc3,
    "sysdesign_uc4": sysdesign_uc4,
}