# -*- coding: utf-8 -*-
"""
Telegram Report Text Guide Bot
----------------------------------------------
This bot helps users who are victims of violations such as unauthorized
release of personal information, harassment, fraud, etc. in Telegram
to find a suitable and official report text to send to Telegram support.

Important: This bot only provides "text templates" to the user. The user
must replace the details (username/link/description of the actual violation)
and should only use it for violations they have witnessed or been a victim of.

Setup:
1. pip install -r requirements.txt
2. Set BOT_TOKEN, WEBSITE_URL, SUPPORT_USERNAME, CHANNEL_USERNAME
   in the config section below (or as environment variables).
3. python bot.py
"""

import os
import logging
import asyncio
import threading

from flask import Flask, jsonify

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# CONFIG - Replace these values with your own information
# ----------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8950711880:AAGR7MfmyvSHpfn2NS_A8I1gwzgPUE0HI2w")
WEBSITE_URL = os.environ.get("WEBSITE_URL", "https://deluxe-fenglisu-ff2ca7.netlify.app/")
SUPPORT_USERNAME = "AlamutTeamir"  # without @
CHANNEL_USERNAME = "Alamutir"  # without @ - channel for forced join
AUTO_DELETE_SECONDS = 10
PORT = int(os.environ.get("PORT", 8080))

# ----------------------------------------------------------------------
# Flask Web Server for Render (Keep-Alive)
# ----------------------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Alamut Bot is running!", 200

@app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": "AlamutReportBot"}), 200

def run_flask():
    """Run Flask app on port for Render"""
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# ----------------------------------------------------------------------
# Violation Categories (matching Telegram's official reporting options)
# key -> display title (Persian for user interface)
# ----------------------------------------------------------------------
CATEGORIES = {
    "spam": "اسپم و تبلیغات مزاحم",
    "violence": "خشونت و تهدید",
    "child_safety": "به خطر افتادن ایمنی کودکان",
    "drugs": "فروش یا تبلیغ مواد غیرقانونی",
    "personal_data": "نقض حریم خصوصی و انتشار اطلاعات شخصی",
    "copyright": "نقض حقوق مالکیت معنوی (کپی‌رایت)",
    "terrorism": "محتوای تروریستی یا افراط‌گرایانه",
    "porn": "محتوای غیراخلاقی یا نامناسب",
    "scam": "کلاهبرداری و فیشینگ",
    "fake_account": "جعل هویت (Impersonation)",
    "other": "سایر تخلفات",
}

CATEGORY_ORDER = [
    "personal_data",
    "scam",
    "fake_account",
    "child_safety",
    "violence",
    "terrorism",
    "drugs",
    "porn",
    "copyright",
    "spam",
    "other",
]

# ----------------------------------------------------------------------
# ENGLISH Report Templates - 10 powerful and long texts for each category
# ----------------------------------------------------------------------
TEMPLATES = {
    "spam": [
        (
            "Dear Telegram Support and Violations Team,\n\n"
            "I am writing to formally report a serious and ongoing violation of Telegram's Terms of Service. "
            "The {type_fa} with ID [ID or link of {type_fa}] has been systematically and continuously "
            "sending massive volumes of unsolicited spam messages, disruptive advertisements, and malicious "
            "content to users. This behavior is not only a clear violation of Telegram's strict anti-spam "
            "policies but also constitutes a significant nuisance that disrupts the user experience and "
            "wastes valuable time and resources of countless Telegram users.\n\n"
            "Despite multiple previous reports and warnings, this {type_fa} has persisted in its harmful "
            "activities and has even escalated its spamming efforts. The content being distributed often "
            "contains deceptive links that may lead to phishing attempts or other security threats. This "
            "sustained abuse of Telegram's platform demonstrates a complete disregard for community "
            "guidelines and user welfare.\n\n"
            "I urgently request that you conduct a thorough investigation into this matter and take "
            "immediate and decisive action against this {type_fa}, including permanent restriction or "
            "complete removal from the platform. Your prompt attention to this serious violation would "
            "be greatly appreciated by all affected users.\n\n"
            "Thank you for your consideration and swift action."
        ),
        (
            "To the Telegram Terms of Service Enforcement Team,\n\n"
            "I am writing to bring to your immediate attention a grave and persistent violation of "
            "Telegram's anti-spam regulations. The {type_fa} identified as [ID or link of {type_fa}] "
            "has been engaged in an organized, systematic campaign of sending unsolicited commercial "
            "messages, spam, and fraudulent content to a vast number of Telegram users. This activity "
            "is not merely an isolated incident but rather a sustained pattern of abuse that has "
            "continued unabated for an extended period.\n\n"
            "The content distributed by this {type_fa} is not only annoying but often contains links "
            "to potentially harmful websites and phishing schemes that could compromise user security "
            "and privacy. The sheer volume of messages being sent suggests the use of automated tools "
            "and bot networks, which constitutes a serious technical violation of Telegram's platform "
            "policies.\n\n"
            "Given the severity and ongoing nature of this violation, I respectfully request that your "
            "team launch an immediate investigation and impose the strongest possible sanctions against "
            "this {type_fa}. This should include permanent account suspension and blocking of all "
            "associated content. The integrity and safety of the Telegram platform depend on swift "
            "action against such abuses.\n\n"
            "I thank you for your professionalism and commitment to maintaining a safe environment for "
            "all Telegram users."
        ),
        (
            "Dear Telegram Security and Content Moderation Team,\n\n"
            "I am reaching out to report a severe and ongoing case of systematic spam abuse on the "
            "Telegram platform. The {type_fa} with identifier [ID or link of {type_fa}] has been "
            "operating as a major source of unsolicited promotional content, spam messages, and "
            "disruptive advertising campaigns that have plagued numerous Telegram users and groups.\n\n"
            "What makes this case particularly concerning is the sophisticated nature of the spamming "
            "techniques being employed. This {type_fa} appears to utilize automated systems and "
            "multiple accounts to circumvent detection mechanisms and maximize its reach. The content "
            "being disseminated often promotes questionable products, dubious services, and in some "
            "cases, outright scams that could cause real financial harm to unsuspecting users.\n\n"
            "The persistence and escalation of these spam activities have created a toxic environment "
            "that undermines trust in the Telegram platform and diminishes the user experience for "
            "millions of legitimate users. The time has come for decisive action against this "
            "persistent offender.\n\n"
            "I strongly urge your team to prioritize this investigation and implement comprehensive "
            "measures to permanently remove this {type_fa} from the platform. Furthermore, I recommend "
            "a thorough review of the methods being used to identify and prevent similar abuse in "
            "the future.\n\n"
            "Thank you for your dedication to maintaining Telegram's integrity and user safety."
        ),
        (
            "To the Telegram Trust and Safety Team,\n\n"
            "I am writing to formally report a serious violation of Telegram's terms regarding "
            "spam and unsolicited commercial communications. The {type_fa} at [ID or link of "
            "{type_fa}] has been identified as a persistent source of spam, fraudulent advertising, "
            "and deceptive content that has been affecting a large number of Telegram users.\n\n"
            "This {type_fa} operates with seeming impunity, continuing its spam campaigns despite "
            "numerous user complaints and reports. The content being distributed includes not only "
            "annoying advertisements but also potentially dangerous links and deceptive offers that "
            "could lead to identity theft, financial loss, or other serious consequences for "
            "unsuspecting users.\n\n"
            "The scale and sophistication of these spam operations suggest a well-organized effort "
            "that requires robust intervention from your team. The continued presence of such "
            "malicious actors on Telegram undermines the platform's credibility and poses a threat "
            "to user safety.\n\n"
            "I respectfully request that you initiate an immediate and thorough investigation into "
            "this {type_fa} and take all necessary measures to prevent further spam dissemination. "
            "This should include permanent account suspension, content removal, and implementation "
            "of measures to prevent similar violations in the future.\n\n"
            "Thank you for your attention to this serious matter."
        ),
        (
            "Dear Telegram Anti-Spam Enforcement Division,\n\n"
            "I am submitting this formal complaint to report an egregious and persistent violation "
            "of Telegram's spam policies. The {type_fa} with the identifier [ID or link of "
            "{type_fa}] has been conducting a sustained campaign of unsolicited messaging that "
            "has affected thousands of Telegram users and groups.\n\n"
            "The methods employed by this {type_fa} are particularly concerning as they appear "
            "to involve sophisticated automation, multiple account usage, and evasion techniques "
            "designed to avoid detection and reporting. The content being pushed ranges from "
            "irritating advertisements to potentially harmful promotions that could deceive "
            "unsuspecting users into sharing personal information or making financial transactions "
            "with fraudulent entities.\n\n"
            "This ongoing abuse represents a significant threat to the Telegram community and "
            "requires immediate and decisive action. The failure to address such violations "
            "effectively not only emboldens the perpetrators but also damages the reputation of "
            "Telegram as a secure and reliable communication platform.\n\n"
            "I urgently request that your team conduct a comprehensive investigation and impose "
            "the strongest possible sanctions against this {type_fa}. Additionally, I recommend "
            "a review of current anti-spam measures to identify potential improvements that could "
            "prevent similar abuse in the future.\n\n"
            "Thank you for your commitment to protecting Telegram users from such harmful activity."
        ),
        (
            "To the Telegram Platform Integrity Team,\n\n"
            "I am writing to report a serious and ongoing violation of Telegram's spam regulations "
            "by the {type_fa} identified as [ID or link of {type_fa}]. This account has been "
            "engaged in persistent spamming activities that have significantly disrupted the user "
            "experience and violated the terms of service governing the platform.\n\n"
            "The scale of this spam operation is substantial, with messages being sent to a wide "
            "range of users and groups. The content often includes deceptive offers, links to "
            "suspicious websites, and promotions for questionable products and services. Many users "
            "have reported receiving multiple messages from this {type_fa} despite blocking and "
            "reporting attempts, indicating a sophisticated approach to evading standard countermeasures.\n\n"
            "Such abuse undermines the fundamental principles of the Telegram platform and erodes "
            "user trust. It is essential that your team takes urgent action to stop these activities "
            "and send a clear message that such violations will not be tolerated.\n\n"
            "I respectfully request that you investigate this matter thoroughly and take all "
            "necessary steps to permanently remove this {type_fa} from the Telegram platform. This "
            "should include comprehensive blocking of all associated content and accounts.\n\n"
            "Thank you for your attention to this urgent matter."
        ),
        (
            "Dear Telegram User Protection Team,\n\n"
            "I am writing to urgently report a persistent and severe violation of Telegram's "
            "anti-spam policies by the {type_fa} located at [ID or link of {type_fa}]. This "
            "account has been identified as a major source of spam and unwanted promotional "
            "content that has been disrupting the Telegram experience for countless users.\n\n"
            "The spam sent by this {type_fa} is not merely an inconvenience but poses real risks "
            "to users. Many messages contain links to phishing sites, promote fraudulent schemes, "
            "or attempt to collect personal information through deceptive means. The persistent "
            "nature of these campaigns suggests a well-resourced operation that requires "
            "significant intervention to dismantle.\n\n"
            "I am deeply concerned about the safety implications of allowing such activities to "
            "continue unchecked. Every day that this {type_fa} remains active, more users are "
            "exposed to potentially harmful content and scams.\n\n"
            "I strongly urge your team to take immediate and decisive action to remove this "
            "{type_fa} from the platform permanently. Additionally, I request that you investigate "
            "whether this is part of a larger network of spam accounts operating on Telegram.\n\n"
            "Thank you for your prompt attention to this critical matter."
        ),
        (
            "To the Telegram Content Moderation and Enforcement Team,\n\n"
            "I am submitting this formal complaint to report a serious and ongoing violation of "
            "Telegram's terms regarding spam and unsolicited commercial content. The {type_fa} "
            "with ID [ID or link of {type_fa}] has been identified as a persistent abuser of the "
            "platform's messaging features.\n\n"
            "This {type_fa} operates with apparent disregard for community guidelines, sending "
            "large volumes of spam messages that clog users' inboxes and create a negative "
            "experience for all Telegram users. The content includes everything from annoying "
            "advertisements to potentially dangerous links that could compromise user security "
            "or lead to financial harm.\n\n"
            "The persistence of this abuse, despite likely being reported by multiple users, "
            "raises concerns about the effectiveness of current enforcement mechanisms. I "
            "respectfully suggest that your team conduct a thorough review and take comprehensive "
            "action to address this case and similar violations.\n\n"
            "I urge you to immediately investigate this {type_fa} and impose the strongest "
            "possible penalties, including permanent account removal and blocking of any "
            "associated content.\n\n"
            "Thank you for your dedication to maintaining a safe and secure Telegram environment."
        ),
        (
            "Dear Telegram Safety and Security Team,\n\n"
            "I am reaching out to report a significant and ongoing violation of Telegram's spam "
            "policies by the {type_fa} identified as [ID or link of {type_fa}]. This account has "
            "been systematically sending unsolicited messages and spam to a wide range of users.\n\n"
            "The content being distributed by this {type_fa} is not only annoying but also "
            "potentially harmful. Many messages appear to be part of scams or phishing attempts "
            "designed to trick users into revealing sensitive information or engaging in fraudulent "
            "financial transactions.\n\n"
            "I am deeply concerned about the impact of such activities on the Telegram community "
            "and the platform's reputation. The presence of persistent spammers undermines trust "
            "and discourages users from engaging fully with the platform.\n\n"
            "I strongly request that your team investigate this matter with urgency and take all "
            "necessary measures to permanently remove this {type_fa} from Telegram. Additionally, "
            "I recommend a review of current spam prevention measures to identify opportunities "
            "for improvement.\n\n"
            "Thank you for your attention to this important matter."
        ),
        (
            "To the Telegram Trust and Safety Division,\n\n"
            "I am writing to report a serious and persistent violation of Telegram's anti-spam "
            "regulations. The {type_fa} with identifier [ID or link of {type_fa}] has been "
            "engaged in extensive spam operations that have affected numerous Telegram users.\n\n"
            "This {type_fa} appears to be part of a larger network of accounts engaged in spam "
            "and potentially malicious activities. The messages sent include unsolicited "
            "advertisements, phishing attempts, and content that could mislead or deceive users.\n\n"
            "The continuation of such activities undermines the integrity of Telegram as a secure "
            "communication platform and exposes users to unnecessary risks. Immediate action is "
            "required to stop these activities and prevent further harm.\n\n"
            "I respectfully request that you conduct a thorough investigation and take all "
            "necessary steps to permanently remove this {type_fa} from Telegram. I also recommend "
            "investigating whether this {type_fa} is connected to a broader network of abusive "
            "accounts.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
    ],
    "violence": [
        (
            "Dear Telegram Safety and Security Team,\n\n"
            "I am writing to urgently report a severe and extremely concerning violation of "
            "Telegram's policies regarding violence and threats. The {type_fa} with ID [ID or "
            "link of {type_fa}] has been actively publishing and distributing content that "
            "contains explicit threats of violence, incitement to harm others, and promotion "
            "of aggressive and dangerous behavior. This is a clear and direct violation of "
            "Telegram's strict policies against violence and threats.\n\n"
            "The content being shared by this {type_fa} is not merely offensive but represents "
            "a genuine threat to the safety and well-being of individuals. It includes direct "
            "threats against specific persons or groups, encouragement of violent actions, and "
            "promotion of harmful ideologies that could lead to real-world violence.\n\n"
            "Given the extremely sensitive nature of this content and the potential for "
            "significant real-world harm, I urgently request that this matter be investigated "
            "with the highest possible priority. The content must be removed immediately, and "
            "this {type_fa} must be permanently banned from the Telegram platform.\n\n"
            "Thank you for your prompt and decisive action in this critical matter."
        ),
        (
            "To the Telegram Trust and Safety Division,\n\n"
            "I am writing to report a serious and ongoing violation of Telegram's policies "
            "against violence and threats. The {type_fa} with the identifier [ID or link of "
            "{type_fa}] has been consistently publishing content that glorifies violence, "
            "makes credible threats against individuals or groups, and promotes activities "
            "that could cause real harm to people.\n\n"
            "This content is not protected by free speech principles as it represents a "
            "clear danger to public safety and individual well-being. The messages and posts "
            "created by this {type_fa} create an atmosphere of fear and intimidation that "
            "makes the Telegram environment unsafe for users.\n\n"
            "I respectfully request that your team launch an immediate investigation and take "
            "all necessary measures to remove this harmful content and permanently ban this "
            "{type_fa} from the platform. The safety of users depends on swift action against "
            "such threats.\n\n"
            "Thank you for your attention to this urgent security concern."
        ),
        (
            "Dear Telegram Content Moderation Team,\n\n"
            "I am submitting this formal complaint to report a serious violation of Telegram's "
            "terms regarding violent content and threats. The {type_fa} at [ID or link of "
            "{type_fa}] has been identified as a source of content that promotes violence, "
            "makes credible threats, and creates a hostile and dangerous environment for users.\n\n"
            "The specific concerns include direct threats against individuals, encouragement "
            "of violent actions, and promotion of ideologies that justify or glorify harm to "
            "others. Such content has no place on Telegram and violates the most fundamental "
            "principles of the platform.\n\n"
            "I strongly urge your team to immediately investigate this {type_fa} and take "
            "decisive action to remove all violent content and permanently ban this account. "
            "Failure to address such serious violations could have severe consequences for "
            "real-world safety.\n\n"
            "Thank you for your prompt attention to this critical matter."
        ),
        (
            "To the Telegram Safety Enforcement Team,\n\n"
            "I am writing to urgently report a serious violation of Telegram's policies "
            "concerning violence, threats, and harmful content. The {type_fa} identified as "
            "[ID or link of {type_fa}] has been actively promoting violence and making "
            "credible threats against individuals and groups.\n\n"
            "The content being distributed by this {type_fa} is extremely concerning and "
            "represents a clear danger to public safety. It includes direct calls for violence, "
            "threats against specific individuals, and promotion of activities that could "
            "cause physical harm.\n\n"
            "I respectfully request that your team initiate an urgent investigation and take "
            "all necessary actions to remove this content and permanently ban this {type_fa} "
            "from Telegram. The safety and security of the Telegram community must be the "
            "highest priority.\n\n"
            "Thank you for your immediate attention to this matter."
        ),
        (
            "Dear Telegram Platform Security Team,\n\n"
            "I am writing to report a severe and ongoing violation of Telegram's terms "
            "regarding violent content and threats. The {type_fa} with ID [ID or link of "
            "{type_fa}] has been consistently publishing content that incites violence, "
            "promotes harm to others, and creates a threatening environment for users.\n\n"
            "The content in question includes explicit threats, encouragement of illegal "
            "activities, and promotion of ideologies that endorse violence as a means to "
            "achieve goals. Such content violates the most basic principles of safety and "
            "respect that Telegram stands for.\n\n"
            "I strongly urge your team to investigate this matter urgently and take decisive "
            "action to remove this {type_fa} from the platform permanently. The presence of "
            "such content undermines the safety and trust that users place in Telegram.\n\n"
            "Thank you for your prompt and effective action."
        ),
        (
            "To the Telegram Trust and Safety Department,\n\n"
            "I am submitting this formal complaint to report a serious violation of Telegram's "
            "policies against violence and threats. The {type_fa} at [ID or link of {type_fa}] "
            "has been identified as a persistent source of violent and threatening content.\n\n"
            "The nature of the content being shared is deeply concerning and represents a "
            "genuine threat to the safety of individuals and the broader Telegram community. "
            "Immediate intervention is required to prevent any potential real-world harm.\n\n"
            "I request that your team conduct a thorough investigation and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} from the platform.\n\n"
            "Thank you for your attention to this urgent matter."
        ),
        (
            "Dear Telegram Safety Moderation Team,\n\n"
            "I am writing to report a serious and ongoing violation of Telegram's content "
            "policies regarding violence and threats. The {type_fa} with identifier [ID or "
            "link of {type_fa}] has been actively publishing content that promotes violence "
            "and makes credible threats against individuals.\n\n"
            "This content creates a hostile and unsafe environment on Telegram and violates "
            "the platform's commitment to providing a secure space for users. The threats "
            "being made could have serious real-world consequences if not addressed promptly.\n\n"
            "I urgently request that your team investigate this matter and take immediate "
            "action to remove all violent content and permanently ban this {type_fa} from "
            "Telegram.\n\n"
            "Thank you for your prompt attention to this critical safety concern."
        ),
        (
            "To the Telegram Content Policy Enforcement Team,\n\n"
            "I am submitting this formal complaint to report a severe violation of Telegram's "
            "terms regarding violence and threats. The {type_fa} identified as [ID or link of "
            "{type_fa}] has been publishing content that incites violence and makes credible "
            "threats against individuals and groups.\n\n"
            "The content being distributed is not only in violation of Telegram's terms but "
            "also poses a genuine risk to public safety. It includes direct calls to violence, "
            "threats against specific individuals, and promotion of harmful ideologies.\n\n"
            "I respectfully request that your team initiate an urgent investigation and take "
            "all necessary actions to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt and effective action in this serious matter."
        ),
        (
            "Dear Telegram User Safety Team,\n\n"
            "I am writing to report a serious and ongoing violation of Telegram's policies "
            "against violence and threatening behavior. The {type_fa} with ID [ID or link of "
            "{type_fa}] has been consistently distributing content that promotes violence "
            "and creates a threatening environment for users.\n\n"
            "The content in question includes explicit threats, encouragement of violent "
            "actions, and promotion of dangerous ideologies. Such content violates Telegram's "
            "terms and poses a real threat to the safety of the community.\n\n"
            "I strongly urge your team to investigate this matter urgently and take decisive "
            "action to remove this {type_fa} from the platform permanently.\n\n"
            "Thank you for your attention to this critical matter."
        ),
        (
            "To the Telegram Security Operations Team,\n\n"
            "I am submitting this formal complaint to report a serious violation of Telegram's "
            "policies regarding violence and threats. The {type_fa} at [ID or link of {type_fa}] "
            "has been identified as a source of violent content and threatening messages.\n\n"
            "This content represents a clear danger to the safety and well-being of individuals "
            "and the broader Telegram community. Immediate action is required to prevent any "
            "potential harm.\n\n"
            "I request that your team conduct a thorough investigation and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} from the platform.\n\n"
            "Thank you for your prompt attention to this urgent matter."
        ),
    ],
    "child_safety": [
        (
            "Dear Telegram Child Safety and Protection Team,\n\n"
            "I am writing to urgently report an extremely serious and deeply concerning "
            "violation of Telegram's most stringent policies regarding child safety and "
            "protection. The {type_fa} with ID [ID or link of {type_fa}] has been found "
            "to contain content that directly endangers the safety, well-being, and "
            "development of children. This is a clear and egregious violation of Telegram's "
            "absolute prohibition of any content that threatens child safety.\n\n"
            "The content in question is deeply disturbing and represents a serious threat to "
            "children's safety. It violates not only Telegram's policies but also fundamental "
            "legal and ethical principles regarding child protection. The presence of such "
            "content on Telegram is completely unacceptable and demands the most urgent and "
            "severe response.\n\n"
            "I urgently request that your team investigate this matter with the highest "
            "possible priority and take immediate and decisive action to remove this content "
            "and permanently ban this {type_fa} from Telegram. Additionally, I strongly "
            "recommend that you escalate this report to the appropriate authorities and "
            "follow up through the official abuse reporting channel at abuse@telegram.org.\n\n"
            "The protection of children must always be the highest priority, and I trust that "
            "your team will act swiftly and decisively in this critical matter.\n\n"
            "Thank you for your immediate attention to this urgent issue."
        ),
        (
            "To the Telegram Trust and Safety Division - Child Protection Unit,\n\n"
            "I am writing to report a grave and deeply concerning violation of Telegram's "
            "child safety policies. The {type_fa} with the identifier [ID or link of "
            "{type_fa}] has been found to contain content that poses a serious risk to "
            "children's safety and well-being.\n\n"
            "This content is completely unacceptable and violates the most fundamental "
            "principles of child protection that Telegram is committed to upholding. It "
            "represents a clear and present danger that requires immediate and decisive "
            "intervention.\n\n"
            "I urgently request that your team launch a comprehensive investigation and "
            "take all necessary measures to remove this content and permanently ban this "
            "{type_fa} from the Telegram platform. I also recommend that this matter be "
            "escalated to the appropriate law enforcement authorities.\n\n"
            "Thank you for your prompt attention to this critical matter."
        ),
        (
            "Dear Telegram Content Moderation and Safety Team,\n\n"
            "I am submitting this formal complaint to report a serious and alarming "
            "violation of Telegram's policies regarding child safety. The {type_fa} at "
            "[ID or link of {type_fa}] has been identified as containing content that "
            "endangers children and violates child protection policies.\n\n"
            "This content is deeply concerning and represents a threat to the safety and "
            "well-being of children. It violates not only Telegram's terms of service but "
            "also international standards for child protection and safety.\n\n"
            "I strongly urge your team to immediately investigate this {type_fa} and take "
            "decisive action to remove all harmful content and permanently ban this account. "
            "The protection of children from such content must be the absolute priority.\n\n"
            "Thank you for your urgent attention to this matter."
        ),
        (
            "To the Telegram Safety and Security Department,\n\n"
            "I am writing to urgently report a serious violation of Telegram's child safety "
            "policies. The {type_fa} identified as [ID or link of {type_fa}] has been found "
            "to contain content that poses a significant risk to the safety and well-being "
            "of children.\n\n"
            "The presence of such content on Telegram is completely unacceptable and "
            "represents a clear violation of the platform's terms and conditions. Immediate "
            "action is required to protect children from exposure to this harmful material.\n\n"
            "I request that your team conduct an urgent investigation and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this critical safety concern."
        ),
        (
            "Dear Telegram Child Protection Enforcement Team,\n\n"
            "I am submitting this formal complaint to report a serious and ongoing violation "
            "of Telegram's child safety policies. The {type_fa} with ID [ID or link of "
            "{type_fa}] has been identified as containing content that endangers children "
            "and violates child protection guidelines.\n\n"
            "This content is deeply concerning and represents a threat to the safety of "
            "children. It violates Telegram's terms of service and international child "
            "protection standards.\n\n"
            "I strongly urge your team to investigate this matter urgently and take decisive "
            "action to remove this content and permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your immediate attention to this important matter."
        ),
        (
            "To the Telegram Trust and Safety Team,\n\n"
            "I am writing to report a grave violation of Telegram's child safety policies "
            "by the {type_fa} at [ID or link of {type_fa}]. This account has been found to "
            "contain content that seriously endangers children's safety and well-being.\n\n"
            "The presence of such content on Telegram is unacceptable and requires immediate "
            "and decisive action to protect children from harm.\n\n"
            "I urgently request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} from the "
            "platform.\n\n"
            "Thank you for your prompt attention to this critical matter."
        ),
        (
            "Dear Telegram Safety Moderation Unit,\n\n"
            "I am submitting this formal complaint to report a serious violation of Telegram's "
            "child protection policies. The {type_fa} with identifier [ID or link of {type_fa}] "
            "has been identified as containing content that poses a significant risk to "
            "children's safety.\n\n"
            "This content is deeply concerning and violates Telegram's commitment to "
            "protecting children from harmful content. Immediate action is required to "
            "address this serious violation.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this critical issue."
        ),
        (
            "To the Telegram Content Safety and Compliance Team,\n\n"
            "I am writing to report a serious and concerning violation of Telegram's child "
            "safety policies. The {type_fa} identified as [ID or link of {type_fa}] has "
            "been found to contain content that endangers children's safety and well-being.\n\n"
            "This content violates Telegram's terms of service and represents a significant "
            "threat to children's safety. Immediate action is required to prevent any "
            "potential harm.\n\n"
            "I strongly urge your team to investigate this matter urgently and take all "
            "necessary measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your immediate attention to this matter."
        ),
        (
            "Dear Telegram User Safety and Child Protection Team,\n\n"
            "I am submitting this formal complaint to report a serious violation of "
            "Telegram's child safety policies. The {type_fa} with ID [ID or link of "
            "{type_fa}] has been identified as containing content that poses a risk to "
            "children's safety and well-being.\n\n"
            "This content is completely unacceptable and represents a violation of "
            "Telegram's terms and child protection guidelines.\n\n"
            "I request that your team conduct an urgent investigation and take all "
            "necessary measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this important matter."
        ),
        (
            "To the Telegram Safety Enforcement Division,\n\n"
            "I am writing to report a serious and urgent violation of Telegram's child "
            "safety policies. The {type_fa} at [ID or link of {type_fa}] has been found "
            "to contain content that endangers children and violates child protection laws.\n\n"
            "The presence of such content on Telegram represents a clear and present danger "
            "that requires immediate and decisive action. The protection of children must "
            "always be the highest priority.\n\n"
            "I urgently request that your team investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this {type_fa} "
            "from the platform.\n\n"
            "Thank you for your prompt attention to this critical issue."
        ),
    ],
    "drugs": [
        (
            "Dear Telegram Support and Enforcement Team,\n\n"
            "I am writing to formally report a serious violation of Telegram's strict "
            "policies regarding the sale and promotion of illegal substances. The {type_fa} "
            "with ID [ID or link of {type_fa}] has been actively engaged in the advertising, "
            "promotion, and facilitation of transactions involving illegal drugs and "
            "controlled substances.\n\n"
            "This activity is not only a clear violation of Telegram's terms of service but "
            "also represents a serious legal concern that could have significant real-world "
            "consequences. The promotion of illegal substances on Telegram undermines the "
            "platform's integrity and poses risks to users who may be exposed to these "
            "dangerous products.\n\n"
            "I urgently request that your team conduct a thorough investigation of this "
            "{type_fa} and take all necessary measures to remove all drug-related content "
            "and permanently ban this account from the Telegram platform.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "To the Telegram Trust and Safety Division,\n\n"
            "I am submitting this formal complaint to report a serious violation of "
            "Telegram's policies against the promotion of illegal substances. The {type_fa} "
            "with the identifier [ID or link of {type_fa}] has been identified as a source "
            "of content that promotes and facilitates the sale of illegal drugs.\n\n"
            "This activity violates Telegram's terms and represents a threat to user safety "
            "and legal compliance. The presence of such content on the platform is "
            "unacceptable and requires immediate intervention.\n\n"
            "I respectfully request that your team investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Content Moderation Team,\n\n"
            "I am writing to report a serious and ongoing violation of Telegram's policies "
            "against the promotion of illegal substances. The {type_fa} at [ID or link of "
            "{type_fa}] has been consistently posting content that advertises and promotes "
            "the sale of illegal drugs.\n\n"
            "This activity is not only a violation of Telegram's terms but also has legal "
            "implications that could affect the platform. The presence of such content "
            "undermines user trust and safety.\n\n"
            "I strongly urge your team to investigate this matter and take all necessary "
            "actions to remove this content and permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your attention to this serious matter."
        ),
        (
            "To the Telegram Safety Enforcement Team,\n\n"
            "I am writing to report a serious violation of Telegram's policies regarding "
            "illegal substances. The {type_fa} identified as [ID or link of {type_fa}] "
            "has been actively promoting and facilitating the sale of illegal drugs.\n\n"
            "This activity violates Telegram's terms and poses risks to users who may be "
            "exposed to harmful substances. Immediate action is required to stop these "
            "illegal activities.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} from "
            "Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Platform Integrity Team,\n\n"
            "I am submitting this formal complaint to report a serious violation of "
            "Telegram's policies against the promotion of illegal substances. The {type_fa} "
            "with ID [ID or link of {type_fa}] has been identified as a source of drug-"
            "related promotional content.\n\n"
            "This activity violates Telegram's terms and represents a threat to user safety "
            "and legal compliance. The promotion of illegal drugs on the platform is "
            "unacceptable and requires immediate action.\n\n"
            "I strongly urge your team to investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "To the Telegram Content Compliance Team,\n\n"
            "I am writing to report a serious violation of Telegram's policies regarding "
            "illegal substances. The {type_fa} at [ID or link of {type_fa}] has been "
            "actively promoting and advertising illegal drugs and controlled substances.\n\n"
            "This activity violates Telegram's terms and could have serious legal "
            "consequences. The presence of such content on the platform is unacceptable.\n\n"
            "I request that your team conduct a thorough investigation and take all "
            "necessary measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your attention to this important matter."
        ),
        (
            "Dear Telegram Safety and Security Department,\n\n"
            "I am submitting this formal complaint to report a serious violation of "
            "Telegram's policies against the promotion of illegal substances. The {type_fa} "
            "with identifier [ID or link of {type_fa}] has been identified as promoting "
            "and facilitating drug sales.\n\n"
            "This activity violates Telegram's terms and poses significant risks to users "
            "and the platform's reputation. Immediate action is required.\n\n"
            "I urge your team to investigate this matter and take all necessary measures "
            "to remove this content and permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Trust and Safety Unit,\n\n"
            "I am writing to report a serious violation of Telegram's policies regarding "
            "illegal substances. The {type_fa} identified as [ID or link of {type_fa}] "
            "has been actively engaged in promoting and advertising illegal drugs.\n\n"
            "This activity is a clear violation of Telegram's terms and poses a threat to "
            "user safety and legal compliance.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} from "
            "Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Content Moderation Division,\n\n"
            "I am submitting this formal complaint to report a serious violation of "
            "Telegram's policies against drug promotion. The {type_fa} with ID [ID or "
            "link of {type_fa}] has been identified as a source of content promoting "
            "illegal substances.\n\n"
            "This activity violates Telegram's terms and represents a risk to user safety. "
            "Immediate action is required to remove this content.\n\n"
            "I strongly urge your team to investigate this matter and take all necessary "
            "measures to permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "To the Telegram Safety Operations Team,\n\n"
            "I am writing to report a serious violation of Telegram's policies regarding "
            "illegal substances. The {type_fa} at [ID or link of {type_fa}] has been "
            "actively engaged in promoting and facilitating drug transactions.\n\n"
            "This activity violates Telegram's terms and could have serious legal and "
            "social consequences. The platform must take immediate action.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} from "
            "Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
    ],
    "personal_data": [
        (
            "Dear Telegram Privacy and Security Team,\n\n"
            "I am writing to formally report a serious and deeply concerning violation "
            "of my personal privacy and Telegram's policies regarding the unauthorized "
            "release of personal information. The {type_fa} with ID [ID or link of "
            "{type_fa}] has published my personal images, contact information, and "
            "other sensitive data without my explicit consent.\n\n"
            "This action constitutes a clear and egregious violation of my privacy "
            "rights and directly contravenes Telegram's strict policies against the "
            "unauthorized sharing of individuals' private information. The publication "
            "of my personal data has caused significant distress and poses a real "
            "threat to my safety and security.\n\n"
            "As the directly affected individual, I urgently request that your team "
            "investigate this matter with the highest priority and take immediate "
            "action to remove all my personal information and permanently ban this "
            "{type_fa} from the Telegram platform.\n\n"
            "Thank you for your prompt attention to this critical privacy matter."
        ),
        (
            "To the Telegram Trust and Privacy Division,\n\n"
            "I am writing to report a serious and ongoing violation of my personal "
            "privacy by the {type_fa} identified as [ID or link of {type_fa}]. This "
            "account has published my personal photographs, phone number, residential "
            "address, and other sensitive information without my authorization.\n\n"
            "This violation has caused me significant emotional distress and creates "
            "a genuine risk to my personal safety and security. The unauthorized "
            "disclosure of my personal information violates Telegram's terms and my "
            "fundamental rights to privacy.\n\n"
            "I respectfully request that your team immediately investigate this "
            "matter and take all necessary measures to remove my personal information "
            "and permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "Dear Telegram Privacy Protection Team,\n\n"
            "I am submitting this formal complaint to report a serious violation of "
            "my privacy rights by the {type_fa} at [ID or link of {type_fa}]. This "
            "account has publicly shared my personal information without my consent "
            "or authorization.\n\n"
            "The information published includes sensitive personal data that could "
            "be used to identify me, contact me, or potentially cause me harm. This "
            "violation of my privacy is deeply distressing and unacceptable.\n\n"
            "I strongly urge your team to investigate this matter urgently and take "
            "all necessary measures to remove my personal information and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this important matter."
        ),
        (
            "To the Telegram Safety and Privacy Department,\n\n"
            "I am writing to report a serious and ongoing violation of my personal "
            "privacy by the {type_fa} identified as [ID or link of {type_fa}]. This "
            "account has published my personal photographs and contact information "
            "without my consent.\n\n"
            "This violation of my privacy causes me significant distress and poses "
            "a real risk to my safety. The unauthorized sharing of my personal data "
            "is a clear violation of Telegram's policies.\n\n"
            "I request that your team conduct an urgent investigation and take all "
            "necessary measures to remove my personal information and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram User Protection Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my privacy rights. The {type_fa} with ID [ID or link of {type_fa}] "
            "has published my personal information without my authorization.\n\n"
            "This violation includes the sharing of sensitive personal data that "
            "could compromise my safety and security. The unauthorized disclosure "
            "of my information violates Telegram's terms and my privacy rights.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove my personal information and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "To the Telegram Privacy Enforcement Unit,\n\n"
            "I am writing to report a serious and ongoing violation of my personal "
            "privacy by the {type_fa} at [ID or link of {type_fa}]. This account "
            "has published my personal information without my consent or knowledge.\n\n"
            "This violation has caused me significant distress and concern for my "
            "safety. The unauthorized sharing of my private data is unacceptable.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove my personal information and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Trust and Safety Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my privacy rights. The {type_fa} with identifier [ID or link of "
            "{type_fa}] has published my personal information without my authorization.\n\n"
            "This violation includes the sharing of sensitive personal data that "
            "could be used to harm me. The unauthorized disclosure of my information "
            "is a clear violation of Telegram's policies.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove my personal information and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Privacy Protection Division,\n\n"
            "I am writing to report a serious and ongoing violation of my personal "
            "privacy by the {type_fa} identified as [ID or link of {type_fa}]. This "
            "account has published my personal photographs and information without "
            "my consent.\n\n"
            "This violation causes me significant emotional distress and poses a "
            "real threat to my safety. The unauthorized sharing of my personal data "
            "violates Telegram's terms.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove my personal information and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram User Safety and Privacy Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my privacy rights. The {type_fa} with ID [ID or link of {type_fa}] "
            "has published my personal information without my authorization.\n\n"
            "This violation includes the sharing of sensitive personal data that "
            "could compromise my safety and security. The unauthorized disclosure "
            "of my information is unacceptable.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove my personal information and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Privacy and Security Department,\n\n"
            "I am writing to report a serious and ongoing violation of my personal "
            "privacy by the {type_fa} at [ID or link of {type_fa}]. This account "
            "has published my personal information without my consent.\n\n"
            "This violation has caused me significant concern for my safety and "
            "well-being. The unauthorized sharing of my private data is a clear "
            "violation of Telegram's policies.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove my personal information and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
    ],
    "copyright": [
        (
            "Dear Telegram Intellectual Property Rights Team,\n\n"
            "I am writing to formally report a serious violation of my copyright "
            "and intellectual property rights by the {type_fa} with ID [ID or link "
            "of {type_fa}]. This account has published and distributed my original "
            "creative work without obtaining my permission or providing attribution.\n\n"
            "As the original creator and copyright holder, I have the exclusive "
            "rights to control the distribution and use of my work. The unauthorized "
            "publication of my content by this {type_fa} is a clear violation of "
            "copyright laws and Telegram's intellectual property policies.\n\n"
            "I respectfully request that your team investigate this matter and "
            "take all necessary measures to remove my copyrighted content and "
            "permanently ban this {type_fa} from the Telegram platform.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Copyright Enforcement Division,\n\n"
            "I am writing to report a serious violation of my intellectual property "
            "rights by the {type_fa} identified as [ID or link of {type_fa}]. This "
            "account has republished my original creative work without my permission.\n\n"
            "The unauthorized distribution of my copyrighted material violates "
            "copyright laws and Telegram's terms of service. I have not granted "
            "any license or permission for this use.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove my copyrighted content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Content Protection Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my copyright by the {type_fa} at [ID or link of {type_fa}]. This "
            "account has published my original creative work without my authorization.\n\n"
            "This violation of my intellectual property rights is a serious matter "
            "that requires immediate action. I have not granted any permission for "
            "my work to be used or distributed.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove my copyrighted content and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Intellectual Property Unit,\n\n"
            "I am writing to report a serious and ongoing violation of my copyright "
            "by the {type_fa} identified as [ID or link of {type_fa}]. This account "
            "has been distributing my original work without permission.\n\n"
            "The unauthorized use of my copyrighted material violates copyright "
            "laws and Telegram's intellectual property policies. I require immediate "
            "action to protect my rights.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove my copyrighted content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Copyright Protection Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my copyright by the {type_fa} with ID [ID or link of {type_fa}]. "
            "This account has published my original work without my permission.\n\n"
            "This violation of my intellectual property rights is unacceptable "
            "and requires immediate action. I have not authorized any use of my "
            "copyrighted material.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove my copyrighted content and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Copyright Enforcement Team,\n\n"
            "I am writing to report a serious violation of my intellectual property "
            "rights by the {type_fa} at [ID or link of {type_fa}]. This account "
            "has republished my original creative work without my authorization.\n\n"
            "This violation of copyright laws is a serious matter that requires "
            "immediate intervention. I have not granted any license for this use.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove my copyrighted content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Intellectual Property Protection Unit,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my copyright by the {type_fa} with identifier [ID or link of "
            "{type_fa}]. This account has published my original work without "
            "my permission.\n\n"
            "This violation of my intellectual property rights is unacceptable "
            "and requires immediate action. I have not authorized any use of my "
            "copyrighted material.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove my copyrighted content and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Content Rights Management Team,\n\n"
            "I am writing to report a serious and ongoing violation of my copyright "
            "by the {type_fa} identified as [ID or link of {type_fa}]. This account "
            "has been distributing my original work without authorization.\n\n"
            "The unauthorized use of my copyrighted material violates copyright "
            "laws and Telegram's intellectual property policies.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove my copyrighted content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Copyright and Content Protection Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my copyright by the {type_fa} with ID [ID or link of {type_fa}]. "
            "This account has published my original creative work without my consent.\n\n"
            "This violation of my intellectual property rights is a serious matter "
            "that requires immediate action from your team.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove my copyrighted content and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Intellectual Property Enforcement Team,\n\n"
            "I am writing to report a serious violation of my copyright by the "
            "{type_fa} at [ID or link of {type_fa}]. This account has published "
            "my original work without obtaining my permission.\n\n"
            "This violation of copyright laws is unacceptable and requires "
            "immediate intervention to protect my intellectual property rights.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove my copyrighted content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
    ],
    "terrorism": [
        (
            "Dear Telegram Safety and Counter-Terrorism Team,\n\n"
            "I am writing to urgently report an extremely serious and alarming "
            "violation of Telegram's policies regarding terrorist and extremist "
            "content. The {type_fa} with ID [ID or link of {type_fa}] has been "
            "actively publishing and promoting content that glorifies terrorism, "
            "supports extremist ideologies, and incites violence for political "
            "or ideological purposes.\n\n"
            "This content represents a clear and present danger to public safety "
            "and violates the most fundamental principles of Telegram's commitment "
            "to providing a safe and secure platform. The promotion of terrorist "
            "ideology on Telegram is completely unacceptable and requires the "
            "most urgent and decisive response.\n\n"
            "I urgently request that your team investigate this matter with the "
            "highest possible priority and take immediate action to remove all "
            "terrorist content and permanently ban this {type_fa} from the Telegram "
            "platform.\n\n"
            "Thank you for your prompt attention to this critical security matter."
        ),
        (
            "To the Telegram Counter-Terrorism and Safety Division,\n\n"
            "I am writing to report a serious and ongoing violation of Telegram's "
            "policies against terrorist and extremist content. The {type_fa} with "
            "the identifier [ID or link of {type_fa}] has been actively promoting "
            "terrorist ideologies and inciting violence.\n\n"
            "The content being distributed by this {type_fa} poses a significant "
            "threat to public safety and violates Telegram's terms of service. The "
            "presence of such content on the platform is unacceptable and requires "
            "immediate action.\n\n"
            "I respectfully request that your team conduct an urgent investigation "
            "and take all necessary measures to remove this terrorist content and "
            "permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this critical matter."
        ),
        (
            "Dear Telegram Content Moderation and Counter-Extremism Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies against terrorist and extremist content. The "
            "{type_fa} at [ID or link of {type_fa}] has been identified as a source "
            "of content that promotes terrorism and extremist ideologies.\n\n"
            "This content is deeply concerning and represents a threat to public "
            "safety and security. The promotion of terrorism on Telegram is a "
            "serious violation of the platform's terms.\n\n"
            "I strongly urge your team to immediately investigate this {type_fa} "
            "and take all necessary measures to remove this content and permanently "
            "ban this account from Telegram.\n\n"
            "Thank you for your prompt attention to this urgent matter."
        ),
        (
            "To the Telegram Security and Counter-Terrorism Department,\n\n"
            "I am writing to urgently report a serious violation of Telegram's "
            "policies regarding terrorist content. The {type_fa} identified as "
            "[ID or link of {type_fa}] has been actively promoting terrorist "
            "ideologies and extremist content.\n\n"
            "This content represents a clear threat to public safety and violates "
            "Telegram's terms of service. Immediate action is required to remove "
            "this content and prevent its spread.\n\n"
            "I request that your team conduct an urgent investigation and take all "
            "necessary measures to remove this content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Counter-Terrorism Enforcement Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies against terrorist content. The {type_fa} with "
            "ID [ID or link of {type_fa}] has been identified as promoting "
            "terrorist ideologies and extremist content.\n\n"
            "The presence of such content on Telegram is unacceptable and requires "
            "immediate intervention. The safety of the community depends on swift "
            "action against such material.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "To the Telegram Trust and Safety Counter-Terrorism Unit,\n\n"
            "I am writing to report a serious and ongoing violation of Telegram's "
            "policies regarding terrorist and extremist content. The {type_fa} at "
            "[ID or link of {type_fa}] has been actively promoting terrorism.\n\n"
            "This content is deeply concerning and represents a threat to public "
            "safety. The promotion of terrorism on Telegram is a serious violation "
            "of the platform's terms.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Counter-Extremism and Safety Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies against terrorist content. The {type_fa} with "
            "identifier [ID or link of {type_fa}] has been identified as a source "
            "of extremist and terrorist content.\n\n"
            "This content violates Telegram's terms and poses a threat to public "
            "safety. Immediate action is required to remove this material.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "To the Telegram Security and Counter-Terrorism Operations Team,\n\n"
            "I am writing to report a serious and urgent violation of Telegram's "
            "policies regarding terrorist content. The {type_fa} identified as "
            "[ID or link of {type_fa}] has been promoting terrorist ideologies.\n\n"
            "This content represents a significant threat to public safety and "
            "violates Telegram's terms of service. Immediate intervention is "
            "required.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this critical matter."
        ),
        (
            "Dear Telegram Content Safety and Counter-Terrorism Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies against terrorist content. The {type_fa} with "
            "ID [ID or link of {type_fa}] has been actively promoting terrorism.\n\n"
            "This content is unacceptable and violates Telegram's terms. The "
            "platform must take immediate action to remove this material.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Counter-Terrorism Enforcement Division,\n\n"
            "I am writing to report a serious violation of Telegram's policies "
            "against terrorist and extremist content. The {type_fa} at [ID or "
            "link of {type_fa}] has been identified as promoting terrorism.\n\n"
            "This content poses a threat to public safety and violates Telegram's "
            "terms. Immediate action is required to address this serious issue.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
    ],
    "porn": [
        (
            "Dear Telegram Content Moderation Team,\n\n"
            "I am writing to formally report a serious violation of Telegram's "
            "policies regarding inappropriate and adult content. The {type_fa} "
            "with ID [ID or link of {type_fa}] has been consistently publishing "
            "and distributing pornographic and obscene content that violates "
            "Telegram's terms of service.\n\n"
            "This content is not only inappropriate but also violates Telegram's "
            "policies on adult content. The presence of such material on the "
            "platform is unacceptable and requires immediate action.\n\n"
            "I respectfully request that your team investigate this matter and "
            "take all necessary measures to remove this content and permanently "
            "ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Trust and Safety Division,\n\n"
            "I am writing to report a serious violation of Telegram's policies "
            "regarding inappropriate content. The {type_fa} with the identifier "
            "[ID or link of {type_fa}] has been publishing obscene and adult "
            "content that violates the platform's terms.\n\n"
            "This content is inappropriate and should not be available on Telegram. "
            "The presence of such material requires immediate intervention.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Content Policy Enforcement Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies regarding adult content. The {type_fa} at "
            "[ID or link of {type_fa}] has been identified as a source of "
            "inappropriate and obscene material.\n\n"
            "This content violates Telegram's terms and is inappropriate for the "
            "platform. Immediate action is required to remove this material.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Content Moderation Department,\n\n"
            "I am writing to report a serious and ongoing violation of Telegram's "
            "policies regarding inappropriate content. The {type_fa} identified "
            "as [ID or link of {type_fa}] has been publishing pornographic material.\n\n"
            "This content violates Telegram's terms and is inappropriate for the "
            "platform. Immediate action is required.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Adult Content Enforcement Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies regarding adult content. The {type_fa} with "
            "ID [ID or link of {type_fa}] has been identified as a source of "
            "pornographic and obscene material.\n\n"
            "This content is inappropriate and violates Telegram's terms of "
            "service. The platform must take immediate action to remove this "
            "material.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Trust and Safety Content Team,\n\n"
            "I am writing to report a serious violation of Telegram's policies "
            "regarding inappropriate content. The {type_fa} at [ID or link of "
            "{type_fa}] has been publishing obscene material that violates the "
            "platform's terms.\n\n"
            "This content is unacceptable and requires immediate action from "
            "your team.\n\n"
            "I request that your team investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Content Moderation Unit,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies regarding adult content. The {type_fa} with "
            "identifier [ID or link of {type_fa}] has been identified as a source "
            "of pornographic material.\n\n"
            "This content violates Telegram's terms and is inappropriate for the "
            "platform. Immediate action is required.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Safety and Content Compliance Team,\n\n"
            "I am writing to report a serious violation of Telegram's policies "
            "regarding inappropriate content. The {type_fa} identified as [ID "
            "or link of {type_fa}] has been publishing obscene material.\n\n"
            "This content violates Telegram's terms and is unacceptable on the "
            "platform. Immediate intervention is required.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Content Enforcement Division,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies regarding adult content. The {type_fa} with "
            "ID [ID or link of {type_fa}] has been identified as a source of "
            "pornographic material.\n\n"
            "This content is inappropriate and violates Telegram's terms of "
            "service. Immediate action is required to remove this material.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this content and permanently ban this "
            "{type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Content Moderation and Policy Team,\n\n"
            "I am writing to report a serious and ongoing violation of Telegram's "
            "policies regarding inappropriate content. The {type_fa} at [ID or "
            "link of {type_fa}] has been publishing obscene material that violates "
            "the platform's terms.\n\n"
            "This content is unacceptable and requires immediate action from your "
            "team to protect the integrity of the platform.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this content and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
    ],
    "scam": [
        (
            "Dear Telegram Fraud and Scam Prevention Team,\n\n"
            "I am writing to formally report a serious and ongoing scam operation "
            "being conducted by the {type_fa} with ID [ID or link of {type_fa}]. "
            "This account has been actively engaging in fraudulent activities, "
            "including phishing attempts, deceptive schemes, and financial scams "
            "designed to defraud unsuspecting Telegram users.\n\n"
            "The methods used by this {type_fa} include false promises, deceptive "
            "offers, and sophisticated techniques to trick users into sharing "
            "sensitive information or making financial transactions with fraudulent "
            "entities. I have personally suffered losses as a result of these "
            "scam operations.\n\n"
            "This ongoing fraud represents a significant threat to the safety and "
            "financial well-being of Telegram users. I urgently request that your "
            "team investigate this matter and take all necessary measures to stop "
            "these scam activities and permanently ban this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "To the Telegram Trust and Safety Anti-Fraud Division,\n\n"
            "I am writing to report a serious and ongoing fraud operation by the "
            "{type_fa} identified as [ID or link of {type_fa}]. This account has "
            "been engaging in deceptive practices and scams that have caused "
            "financial harm to users.\n\n"
            "The scam tactics used by this {type_fa} are sophisticated and have "
            "deceived numerous users. This activity violates Telegram's terms and "
            "poses a significant risk to user safety.\n\n"
            "I respectfully request that your team conduct an urgent investigation "
            "and take all necessary measures to remove this {type_fa} and prevent "
            "further fraud.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Financial Safety and Security Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies against fraud and scams. The {type_fa} at "
            "[ID or link of {type_fa}] has been identified as a source of "
            "fraudulent activities and financial scams.\n\n"
            "This {type_fa} has been using deceptive techniques to defraud users "
            "and cause financial harm. The activities are a clear violation of "
            "Telegram's terms and pose a threat to user safety.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to stop these scam activities and permanently ban "
            "this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "To the Telegram Anti-Scam Enforcement Team,\n\n"
            "I am writing to report a serious and ongoing scam operation by the "
            "{type_fa} identified as [ID or link of {type_fa}]. This account has "
            "been actively defrauding users through deceptive practices.\n\n"
            "The scam activities conducted by this {type_fa} have caused significant "
            "financial harm to users and violate Telegram's terms of service.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to stop these activities and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram User Protection and Anti-Fraud Team,\n\n"
            "I am submitting this formal complaint to report a serious scam operation "
            "by the {type_fa} with ID [ID or link of {type_fa}]. This account has "
            "been engaging in fraudulent activities and causing financial harm.\n\n"
            "The deceptive practices used by this {type_fa} are sophisticated and "
            "have affected numerous users. This activity violates Telegram's terms.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Fraud Investigation Unit,\n\n"
            "I am writing to report a serious and ongoing scam operation by the "
            "{type_fa} at [ID or link of {type_fa}]. This account has been "
            "conducting fraudulent activities that have caused financial losses.\n\n"
            "The scam techniques employed by this {type_fa} are designed to deceive "
            "and defraud users. This is a clear violation of Telegram's terms.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to stop these activities and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Security and Anti-Scam Department,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies against fraud and scams. The {type_fa} with "
            "identifier [ID or link of {type_fa}] has been identified as a source "
            "of scam activities.\n\n"
            "This {type_fa} has been using deceptive tactics to defraud users and "
            "cause financial harm. This activity is unacceptable and requires "
            "immediate action.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Trust and Safety Anti-Fraud Unit,\n\n"
            "I am writing to report a serious and ongoing fraud operation by the "
            "{type_fa} identified as [ID or link of {type_fa}]. This account has "
            "been engaging in deceptive practices that harm users.\n\n"
            "The scam activities conducted by this {type_fa} violate Telegram's "
            "terms and pose a significant threat to user safety.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to stop these activities and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Financial Protection Team,\n\n"
            "I am submitting this formal complaint to report a serious scam "
            "operation by the {type_fa} with ID [ID or link of {type_fa}]. This "
            "account has been defrauding users through deceptive practices.\n\n"
            "The fraud activities conducted by this {type_fa} have caused financial "
            "harm and violate Telegram's terms of service.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this {type_fa} from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Anti-Fraud Enforcement Division,\n\n"
            "I am writing to report a serious and ongoing scam operation by the "
            "{type_fa} at [ID or link of {type_fa}]. This account has been "
            "engaged in fraudulent activities that harm users.\n\n"
            "The scam techniques used by this {type_fa} are deceptive and cause "
            "financial harm. This is a clear violation of Telegram's terms.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to stop these activities and permanently ban this {type_fa} "
            "from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
    ],
    "fake_account": [
        (
            "Dear Telegram Identity Protection Team,\n\n"
            "I am writing to formally report a serious violation of my identity "
            "and personal reputation by the {type_fa} with ID [ID or link of "
            "{type_fa}]. This account has been impersonating me and using my "
            "identity without my permission to interact with other users.\n\n"
            "The fake account is presenting itself as me and causing significant "
            "confusion and potential harm to my reputation. This identity theft "
            "violates Telegram's policies against impersonation and causes me "
            "serious distress.\n\n"
            "I respectfully request that your team investigate this matter and "
            "take all necessary measures to remove this fake account and "
            "permanently ban it from Telegram.\n\n"
            "Thank you for your prompt attention to this serious matter."
        ),
        (
            "To the Telegram Trust and Identity Protection Unit,\n\n"
            "I am writing to report a serious violation of my identity by the "
            "{type_fa} identified as [ID or link of {type_fa}]. This account is "
            "impersonating me and causing reputational harm.\n\n"
            "The fake account is using my name and photos to mislead other users. "
            "This identity theft violates Telegram's terms and causes me distress.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this fake account and permanently ban it from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Anti-Impersonation Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my identity by the {type_fa} at [ID or link of {type_fa}]. This "
            "account has been impersonating me without my permission.\n\n"
            "The fake account is causing confusion and potential harm to my "
            "personal reputation. This identity theft is a clear violation of "
            "Telegram's policies.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this fake account and permanently ban "
            "it from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Identity Theft Enforcement Team,\n\n"
            "I am writing to report a serious and ongoing violation of my identity "
            "by the {type_fa} identified as [ID or link of {type_fa}]. This "
            "account has been impersonating me and damaging my reputation.\n\n"
            "The fake account is using my identity to interact with other users "
            "without my authorization. This violates Telegram's terms.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this fake account and permanently ban it from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Identity Protection and Safety Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my identity by the {type_fa} with ID [ID or link of {type_fa}]. "
            "This account has been impersonating me without my consent.\n\n"
            "The fake account is causing damage to my reputation and creating "
            "confusion among my contacts. This identity theft is unacceptable.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this fake account and permanently ban "
            "it from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Anti-Impersonation Division,\n\n"
            "I am writing to report a serious and ongoing violation of my identity "
            "by the {type_fa} at [ID or link of {type_fa}]. This account has been "
            "impersonating me and causing reputational harm.\n\n"
            "The fake account is using my identity without authorization, violating "
            "Telegram's policies against impersonation.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this fake account and permanently ban it from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Identity Fraud Prevention Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my identity by the {type_fa} with identifier [ID or link of "
            "{type_fa}]. This account has been impersonating me without my consent.\n\n"
            "The fake account is damaging my reputation and misleading other users. "
            "This identity theft is a clear violation of Telegram's terms.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this fake account and permanently ban "
            "it from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Trust and Identity Protection Team,\n\n"
            "I am writing to report a serious violation of my identity by the "
            "{type_fa} identified as [ID or link of {type_fa}]. This account is "
            "impersonating me and causing reputational damage.\n\n"
            "The fake account is using my identity without authorization, violating "
            "Telegram's policies against impersonation.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this fake account and permanently ban it from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "Dear Telegram Identity Security Team,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of my identity by the {type_fa} with ID [ID or link of {type_fa}]. "
            "This account has been impersonating me and harming my reputation.\n\n"
            "The fake account is misleading other users and causing confusion. "
            "This identity theft is a serious violation of Telegram's terms.\n\n"
            "I strongly urge your team to investigate this matter and take all "
            "necessary measures to remove this fake account and permanently ban "
            "it from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Anti-Identity Theft Team,\n\n"
            "I am writing to report a serious and ongoing violation of my identity "
            "by the {type_fa} at [ID or link of {type_fa}]. This account has been "
            "impersonating me without my permission.\n\n"
            "The fake account is causing significant reputational harm and confusion "
            "among my contacts. This identity theft violates Telegram's policies.\n\n"
            "I request that your team investigate this matter and take all necessary "
            "measures to remove this fake account and permanently ban it from Telegram.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
    ],
    "other": [
        (
            "Dear Telegram Support and Violations Team,\n\n"
            "I am writing to formally report a serious violation of Telegram's "
            "Terms of Service by the {type_fa} with ID [ID or link of {type_fa}]. "
            "The specific violation involves: [Please provide a detailed and "
            "accurate description of the violation here].\n\n"
            "This activity clearly violates Telegram's terms and policies, and "
            "represents a serious concern that requires immediate investigation "
            "and action. The behavior in question has caused significant distress "
            "and concern.\n\n"
            "I respectfully request that your team investigate this matter "
            "thoroughly and take all necessary measures to address this violation "
            "and prevent its recurrence.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
        (
            "To the Telegram Trust and Safety Division,\n\n"
            "I am submitting this formal complaint to report a serious violation "
            "of Telegram's policies by the {type_fa} identified as [ID or link "
            "of {type_fa}]. The violation in question is: [Please provide a "
            "detailed and accurate description of the violation here].\n\n"
            "This activity is inconsistent with Telegram's terms and policies, "
            "and requires immediate investigation and action. The behavior has "
            "caused significant concern and potential harm.\n\n"
            "I request that your team investigate this matter and take all "
            "necessary measures to address this violation and prevent its "
            "recurrence.\n\n"
            "Thank you for your prompt attention to this matter."
        ),
    ],
}

TYPE_FA = {"channel": "channel", "group": "group"}


# ----------------------------------------------------------------------
# Keyboard Pages
# ----------------------------------------------------------------------
# Telegram's default colors for buttons (from Bot API 9.4 onwards):
# "primary" = blue, "success" = green, "danger" = red
SENSITIVE_CATEGORIES = {"personal_data", "child_safety", "violence", "terrorism", "scam", "fake_account"}


def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("Ready Text", callback_data="menu_ready", style="primary")],
        [InlineKeyboardButton("About Us", callback_data="menu_about", style="primary")],
        [InlineKeyboardButton("Alamut Website", url=WEBSITE_URL, style="primary")],
        [InlineKeyboardButton("Support", url=f"https://t.me/{SUPPORT_USERNAME}", style="success")],
    ]
    return InlineKeyboardMarkup(rows)


def join_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("Join the Channel", url=f"https://t.me/{CHANNEL_USERNAME}", style="success")],
        [InlineKeyboardButton("Check Membership", callback_data="check_membership", style="primary")],
    ]
    return InlineKeyboardMarkup(rows)


def ready_text_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("Text for Channel", callback_data="type_channel_ready", style="primary")],
        [InlineKeyboardButton("Text for Group", callback_data="type_group_ready", style="primary")],
        [InlineKeyboardButton("Back", callback_data="back_main", style="danger")],
    ]
    return InlineKeyboardMarkup(rows)


def category_keyboard(target_type: str, mode: str) -> InlineKeyboardMarkup:
    rows = []
    # Create rows with 2 buttons per row for better layout
    temp_list = []
    for key in CATEGORY_ORDER:
        title = CATEGORIES[key]
        style = "danger" if key in SENSITIVE_CATEGORIES else "primary"
        temp_list.append(InlineKeyboardButton(title, callback_data=f"cat:{target_type}:{key}:{mode}", style=style))
        if len(temp_list) == 2:
            rows.append(temp_list)
            temp_list = []
    if temp_list:
        rows.append(temp_list)
    rows.append([InlineKeyboardButton("Back", callback_data=f"back_mode:{mode}", style="danger")])
    return InlineKeyboardMarkup(rows)


def text_list_keyboard(target_type: str, category: str, mode: str) -> InlineKeyboardMarkup:
    count = len(TEMPLATES[category])
    rows = []
    # Create rows with 2 buttons per row for better layout
    temp_list = []
    for i in range(1, count + 1):
        temp_list.append(
            InlineKeyboardButton(
                f"Text {i}",
                callback_data=f"txt:{target_type}:{category}:{i}:{mode}",
                style="success",
            )
        )
        if len(temp_list) == 2:
            rows.append(temp_list)
            temp_list = []
    if temp_list:
        rows.append(temp_list)
    rows.append(
        [InlineKeyboardButton("Back", callback_data=f"backcat:{target_type}:{mode}", style="danger")]
    )
    return InlineKeyboardMarkup(rows)


def back_only_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Back", callback_data=callback_data, style="danger")]]
    )


# ----------------------------------------------------------------------
# Static menu texts
# ----------------------------------------------------------------------
JOIN_MESSAGE_EN = (
    "The punishment for oppression of the oppressed is death.\n\n"
    "This bot is designed to help you obtain ready-made report templates for reporting "
    "violations and abusive behavior on Telegram. You can use these templates to file "
    "reports against violating channels and groups that engage in:\n\n"
    "- Spreading spam and harassment\n"
    "- Privacy violations and sharing personal information\n"
    "- Fraud and scams\n"
    "- Identity theft and impersonation\n"
    "- Violence and threats\n"
    "- Child safety violations\n"
    "- Drug promotion\n"
    "- Terrorist content\n"
    "- Inappropriate content\n"
    "- Copyright infringement\n"
    "- And other violations of Telegram's Terms of Service\n\n"
    "You can also stay informed about the latest news and updates on our website:\n"
    "Alamut Website: {website_url}\n\n"
    "For reporting non-Islamic websites, websites that disclose personal information, "
    "or violating private support accounts, please contact our support team directly.\n\n"
    "Please join our channel to access the bot's features."
)

JOIN_MESSAGE_FA = (
    "سزای ظلم به مظلوم مرگ است.\n\n"
    "این ربات برای کمک به شما در تهیه الگوهای گزارش آماده برای گزارش تخلفات و رفتارهای سوء در تلگرام طراحی شده است. "
    "شما می‌توانید از این الگوها برای ثبت گزارش علیه کانال‌ها و گروه‌های متخلف که در موارد زیر فعالیت دارند، استفاده کنید:\n\n"
    "- انتشار اسپم و آزار\n"
    "- نقض حریم خصوصی و انتشار اطلاعات شخصی\n"
    "- کلاهبرداری و فیشینگ\n"
    "- جعل هویت\n"
    "- خشونت و تهدید\n"
    "- به خطر انداختن ایمنی کودکان\n"
    "- تبلیغ مواد مخدر\n"
    "- محتوای تروریستی\n"
    "- محتوای نامناسب\n"
    "- نقض کپی‌رایت\n"
    "- و سایر تخلفات از قوانین تلگرام\n\n"
    "همچنین می‌توانید از آخرین اخبار و به‌روزرسانی‌ها در وب‌سایت ما مطلع شوید:\n"
    "وب‌سایت الموت: {website_url}\n\n"
    "برای گزارش سایت‌های غیراسلامی، سایت‌های افشای اطلاعات شخصی یا حساب‌های پشتیبانی متخلف، لطفاً مستقیماً با تیم پشتیبانی ما تماس بگیرید.\n\n"
    "لطفاً برای دسترسی به امکانات ربات، در کانال ما عضو شوید."
)

JOIN_MESSAGE = JOIN_MESSAGE_EN + "\n\n" + "-" * 40 + "\n\n" + JOIN_MESSAGE_FA

MAIN_MENU_TEXT = (
    "Welcome to Alamut Bot.\n\n"
    "Through the buttons below, you can obtain ready-made text for writing "
    "violation reports on Telegram, visit the Alamut website, or get in touch "
    "with support."
)

READY_TEXT_MENU_TEXT = (
    "Please specify whether the report text is for a channel or a group."
)

CATEGORY_MENU_TEXT = "Please select the type of violation from the list below."

TEXT_LIST_MENU_TEXT = "Please select one of the ready-made texts below."

DELETE_NOTICE = (
    "Note: This message will be automatically deleted after {AUTO_DELETE_SECONDS} seconds. "
    "If you need it, please copy the text now."
)

ABOUT_TEXT = (
    "درباره ربات الموت\n\n"
    "این ربات با هدف کمک به کاربران تلگرام در تهیه گزارش‌های رسمی و حرفه‌ای برای تخلفات مختلف طراحی شده است.\n\n"
    "ویژگی‌های ربات:\n"
    "- ارائه الگوهای گزارش آماده برای انواع تخلفات\n"
    "- امکان انتخاب بین ۱۰ متن مختلف برای هر دسته تخلف\n"
    "- گزارش‌های حرفه‌ای و قوی با لحنی رسمی و محکم\n"
    "- پشتیبانی از گزارش برای کانال‌ها و گروه‌ها\n"
    "- حذف خودکار پیام‌های گزارش پس از ۱۰ ثانیه برای حفظ امنیت\n\n"
    "این ربات توسط تیم الموت توسعه داده شده است.\n"
    "برای ارتباط با پشتیبانی، از دکمه Support در منوی اصلی استفاده کنید.\n"
    "همچنین می‌توانید از وب‌سایت الموت برای مشاهده اخبار و به‌روزرسانی‌ها استفاده کنید."
)


# ----------------------------------------------------------------------
# Handlers
# ----------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            await update.message.reply_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())
        else:
            join_text = JOIN_MESSAGE.format(website_url=WEBSITE_URL)
            await update.message.reply_text(join_text, reply_markup=join_keyboard())
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        join_text = JOIN_MESSAGE.format(website_url=WEBSITE_URL)
        await update.message.reply_text(join_text, reply_markup=join_keyboard())


async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    try:
        chat_member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            await query.edit_message_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())
        else:
            await query.answer("You have not joined the channel yet. Please join first.", show_alert=True)
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        await query.answer("Please join the channel first and try again.", show_alert=True)


async def delete_message_later(context: ContextTypes.DEFAULT_TYPE):
    """حذف پیام بعد از زمان مشخص"""
    job = context.job
    chat_id, message_id = job.data
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"✅ Deleted message {message_id} in chat {chat_id}")
    except Exception as exc:
        logger.warning(f"Could not delete message {message_id} in chat {chat_id}: {exc}")


async def delete_notice_later(context: ContextTypes.DEFAULT_TYPE):
    """حذف پیام هشدار بعد از زمان مشخص"""
    job = context.job
    chat_id, message_id = job.data
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"✅ Deleted notice {message_id} in chat {chat_id}")
    except Exception as exc:
        logger.warning(f"Could not delete notice {message_id} in chat {chat_id}: {exc}")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "check_membership":
        await check_membership(update, context)
        return

    # Check membership for any action
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if chat_member.status not in ["member", "administrator", "creator"]:
            join_text = JOIN_MESSAGE.format(website_url=WEBSITE_URL)
            await query.edit_message_text(join_text, reply_markup=join_keyboard())
            return
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        join_text = JOIN_MESSAGE.format(website_url=WEBSITE_URL)
        await query.edit_message_text(join_text, reply_markup=join_keyboard())
        return

    if data == "back_main":
        await query.edit_message_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())
        return

    if data == "menu_ready":
        await query.edit_message_text(READY_TEXT_MENU_TEXT, reply_markup=ready_text_keyboard())
        return

    if data == "menu_about":
        await query.edit_message_text(ABOUT_TEXT, reply_markup=back_only_keyboard("back_main"))
        return

    if data in ("type_channel_ready", "type_group_ready"):
        target_type = "channel" if data == "type_channel_ready" else "group"
        await query.edit_message_text(
            CATEGORY_MENU_TEXT, reply_markup=category_keyboard(target_type, "ready")
        )
        return

    if data.startswith("back_mode:"):
        _, mode = data.split(":")
        if mode == "ready":
            await query.edit_message_text(READY_TEXT_MENU_TEXT, reply_markup=ready_text_keyboard())
        else:
            await query.edit_message_text(READY_TEXT_MENU_TEXT, reply_markup=ready_text_keyboard())
        return

    if data.startswith("backcat:"):
        _, target_type, mode = data.split(":")
        await query.edit_message_text(
            CATEGORY_MENU_TEXT, reply_markup=category_keyboard(target_type, "ready")
        )
        return

    if data.startswith("cat:"):
        _, target_type, category, mode = data.split(":")
        await query.edit_message_text(
            TEXT_LIST_MENU_TEXT, reply_markup=text_list_keyboard(target_type, category, "ready")
        )
        return

    if data.startswith("txt:"):
        _, target_type, category, idx_str, mode = data.split(":")
        idx = int(idx_str) - 1
        template = TEMPLATES[category][idx]
        type_fa = TYPE_FA[target_type]
        final_text = template.format(type_fa=type_fa)

        # Send the report text
        sent_message = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=final_text,
            reply_markup=back_only_keyboard(f"backcat:{target_type}:ready"),
        )

        # Send delete notice as a separate message
        notice_text = DELETE_NOTICE.format(AUTO_DELETE_SECONDS=AUTO_DELETE_SECONDS)
        notice_message = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=notice_text,
        )

        # Schedule deletion of both messages using JobQueue
        try:
            context.job_queue.run_once(
                delete_message_later,
                when=AUTO_DELETE_SECONDS,
                data=(sent_message.chat_id, sent_message.message_id),
            )
            context.job_queue.run_once(
                delete_notice_later,
                when=AUTO_DELETE_SECONDS,
                data=(notice_message.chat_id, notice_message.message_id),
            )
            logger.info(f"⏰ Scheduled deletion for messages in {AUTO_DELETE_SECONDS} seconds")
        except Exception as e:
            logger.error(f"❌ Failed to schedule deletion: {e}")
        
        return


async def post_init(application: Application):
    """This runs after the Application is initialized"""
    logger.info("✅ Bot is ready and JobQueue is active!")


def main():
    if BOT_TOKEN == "PUT-YOUR-BOT-TOKEN-HERE":
        raise RuntimeError(
            "Please set BOT_TOKEN in bot.py or as an environment variable."
        )

    # Start Flask server in a separate thread (for Render keep-alive)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("🌐 Flask web server started on port 8080 for Render keep-alive")

    # Create Application with JobQueue properly initialized
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(check_membership, pattern="^check_membership$"))

    logger.info("🤖 Bot is starting with Polling + Keep-Alive...")
    
    # ✅ ساده‌ترین حالت ممکن - بدون پارامترهای اضافی
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
